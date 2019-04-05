import site

from django.shortcuts import render
from django.views.generic import View
from identity.util import validate_domain
from identity.models import Identity, Service, ServiceThirdPartyEmbeds
from identity.filters import ServiceFilter
from identity.tables import ServiceTable
from mailfetcher.models import Mail, Eresource, Thirdparty
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from django.shortcuts import redirect
from django.db.models import Count
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from mailfetcher import analyser_cron
from . import forms
from mailfetcher.analyser_cron import create_service_cache
from identity import checks
import logging
import time

# Get named logger
logger = logging.getLogger(__name__)


class HomeView(View):
    def get_last_services(self):
        idents = Identity.objects.filter(approved=True)
        return Service.objects.filter(identity__in=idents).distinct().order_by('-id')[:10]

    def get_common_trackhosts(self):
        return Thirdparty.objects.filter(eresource__type='con').annotate(
            num_service=Count('eresource__mail__identity__service', distinct=True)).order_by('-num_service')[:10]

    def get_global_stats(self):
        return {
            "email_count": Mail.objects.count(),
            "service_count": Service.objects.count(),  # TODO Ensure that service has at least 1 confirmed ident
            "tracker_count": Thirdparty.objects.count()  # TODO Model will be renamed on merge
        }

    def post(self, request, *args, **kwargs):
        def abort_with_error(title, error, domain):
            """Abort processing and show error in frontend"""
            return render(request, "home.html", {'notification': {"message": error,
                                                                  "title": title,
                                                                  "domain": domain},
                                                 'global_stats': self.get_global_stats()})

        def offer_identity_creation(domain):
            """Offer the user the option to create a new identity for the provided domain"""
            return render(request, "home.html", {'offer_identity_creation': domain,
                                                 'global_stats': self.get_global_stats()})
        # Get the requested domain from the POST request
        try:
            domain = request.POST['domain']
            # Format domain. Will also ensure that the domain is valid, and return None on invalid domains
            domain = validate_domain(domain)
        except KeyError:
            # Someone is messing with us. Log this.
            logger.warning('HomeView.post: Malformed POST request received', extra={'request': request})
            # Send them back to the homepage with a slap on the wrist
            return abort_with_error(_("Internal error"), _("You sent a request the server did not understand. Please try again, or contact us if the problem persists."), domain)
        except AssertionError:
            # Someone may be messing with us. Save it, just in case.
            logger.info("HomeView.post: Invalid URL passed", extra={'request': request, 'domain': domain})
            # Send them back to the homepage with a slap on the wrist
            return abort_with_error(_("Invalid Address"), _("This does not look like a website - please try again"), domain)

        # See if we already have it in the database
        try:
            service = Service.objects.get(url=domain)
        except ObjectDoesNotExist:
            return offer_identity_creation(domain)

        # Return results by forwarding to service URL with identifer
        return redirect('Service', service=service.id)

    def get(self, request, *args, **kwargs):
        # Get the last approved services

        return render(request, "home.html", {'global_stats': self.get_global_stats()})


class IdentityView(View):
    def post(self, request, *args, **kwargs):
        try:
            domain = request.POST['domain']
            # Format domain. Will also ensure that the domain is valid, and return None on invalid domains
            domain = validate_domain(domain)
        except KeyError:
            # Someone is messing with us. Log this.
            logger.warning('IdentityView.post: Malformed POST request received', extra={'request': request})
            # Send them back to the homepage with a slap on the wrist
            # TODO: Add code to display a warning on homepage
            return redirect('Home')
        # Check if people are messing with us
        except AssertionError:
            # Someone may be messing with us. Save it, just in case.
            logger.info("IdentityView.post: Invalid URL passed", extra={'request': request, 'domain': domain})
            # Send them back to the homepage with a slap on the wrist
            # TODO: Add code to display a warning on homepage
            return redirect('Home')

        # Get or create service
        service, created = Service.objects.get_or_create(url=domain, name=domain)
        service.save()

        # Select a domain to use for the identity
        # TODO this is a strange piece of code - if the break is never hit, it will create all further domains
        # with the last domain from the list? Double-check
        for mailcred in settings.MAILCREDENTIALS:
            identityDomain = mailcred['DOMAIN']
            if Identity.objects.filter(service_id=service.pk).filter(mail__contains=identityDomain).count() == 0:
                break

        # Create an identity and save it
        ident = Identity.create(service, identityDomain)
        ident.save()

        if created:
            create_service_cache(service, force=True)

        # Display the result to the user
        return render(request, 'identity/identity.html', {'ident': ident})


class ServiceView(View):
    def get(self, request, *args, **kwargs):
        # Check if the kwarg is even set
        try:
            sid = kwargs['service']
        except KeyError:
            # No service kwarg is set, warn
            logger.info('ServiceView.get: Malformed GET request received', extra={'request': request})
            # TODO: Add code to display a warning on homepage
            return redirect('Home')

        try:
            service = Service.objects.get(id=sid)
        except ObjectDoesNotExist:
            logger.info("ServiceView.get: Invalid service requested", extra={'request': request, 'service_id': sid})
            # TODO: Add code to display a warning on homepage
            return redirect('Home')
        return self.render_service(request, service)

    @staticmethod
    def render_service(request, service, form=None):

        site_params = ServiceView.get_service_site_params(service)
        if site_params is None:
            logger.warn("ServiceView.render_service: Cache miss", extra={'request': request, 'service_id': service.id})
            # Display a warning that the cache isn't up to date
            # TODO We probably also want to mark the service as dirty to ensure its generated, just in case stuff went wrong somewhere
            return render(request, 'identity/service.html', {"error": "cache miss", "service": service})

        # Render the site
        if form is None:
            site_params['form'] = forms.ServiceMetadataForm(instance=service)
        else:
            site_params['form'] = form
        site_params['service'] = service
        site_params['checks'] = []

        # Run checks
        for check in checks.SERVICE_CHECKS:
            site_params['checks'].append(check(site_params))
        return render(request, 'identity/service.html', site_params)

    @staticmethod
    def get_service_site_params(service, force_makecache=False):
        start_time = time.time()
        if force_makecache:
            analyser_cron.create_service_cache(service, force=True)
        site_params = cache.get(service.derive_service_cache_path())

        if site_params is None:
            return None

        # All identities of the service
        identities = Identity.objects.filter(service=service)
        emails = Mail.objects.filter(identity__in=identities, identity__approved=True).distinct()
        service_3p_conns = ServiceThirdPartyEmbeds.objects.filter(service=service)
        third_party_conns_setting_cookies = service_3p_conns.filter(sets_cookie=True)
        third_parties = service.thirdparties.distinct()

        site_params['service'] = service
        site_params['idents'] = identities
        site_params['count_mails'] = emails.count()
        site_params['unconfirmed_idents'] = identities.filter(approved=False)
        site_params['sets_cookies'] = third_party_conns_setting_cookies.exists()
        site_params['num_different_thirdparties'] = third_parties.count()
        site_params['leaks_address'] = service_3p_conns.filter(leaks_address=True).exists()

        end_time = time.time()
        print('Get service_site_params took: {}s'.format(end_time - start_time))
        return site_params


class ServiceMetaView(View):
    def post(self, request, *args, **kwargs):
        try:
            sid = request.POST['serviceID']
            if str(sid) != str(kwargs['service']):
                # Someone is messing with us
                logger.warn('ServiceMetaView.post: Provided service did not match POSTed service', extra={'request': request, "providedID": kwargs["service"], "postID": sid})
                return redirect('Home')
            # Get service from database
            service = Service.objects.get(id=sid)
        except KeyError:
            # No service kwarg is set, warn
            logger.warn('ServiceMetaView.post: Malformed POST request received', extra={'request': request})
            # TODO: Add code to display a warning on homepage
            return redirect('Home')
        except ObjectDoesNotExist:
            logger.warn('ServiceMetaView.post: POST request for non-existing service', extra={'request': request})
            return redirect('Home')

        form = forms.ServiceMetadataForm(request.POST)
        if not form.is_valid():
            logger.info('ServiceMetaView.post: Invalid data submitted on metadata form', extra={'request': request, 'form': form})
            return ServiceView.render(request, service, form)

        # Form is valid
        sector = form.cleaned_data['sector']
        country = form.cleaned_data['country_of_origin']
        service.country_of_origin = country
        service.sector = sector
        service.save()
        return redirect('Service', service=service.id)


class ServiceListView(SingleTableMixin, FilterView):
    model = Service
    table_class = ServiceTable
    template_name = "service_filter.html"
    paginate_by = 25
    filterset_class = ServiceFilter


class EmbedView(View):
    def get(self, request, *args, **kwargs):
        # Check if the kwarg is even set
        try:
            sid = kwargs['embed']
        except KeyError:
            # No service kwarg is set, warn
            logger.info('EmbedView.get: Malformed GET request received', extra={'request': request})
            # TODO: Add code to display a warning on homepage
            return redirect('Home')

        try:
            embed = Thirdparty.objects.get(id=sid)
        except ObjectDoesNotExist:
            logger.info("EmbedView.get: Invalid service requested", extra={'request': request, 'service_id': sid})
            # TODO: Add code to display a warning on homepage
            return redirect('Home')
        return self.render_embed(request, embed)

    @staticmethod
    def render_embed(request, embed, form=None):

        site_params = EmbedView.get_embed_site_params(embed)
        if site_params is None:
            logger.warn("EmbedView.render_embed: Cache miss", extra={'request': request, 'embed_id': embed.id})
            # Display a warning that the cache isn't up to date
            # TODO We probably also want to mark the embed as dirty to ensure its generated, just in case stuff went wrong somewhere
            return render(request, 'identity/embed.html', {"error": "cache miss", "embed": embed})

        # Render the site
        if form is None:
            site_params['form'] = forms.EmbedMetadataForm(instance=embed)
        else:
            site_params['form'] = form

        site_params['embed'] = embed

        site_params['checks'] = []
        # Add any checks that should be run on embeds
        for check in checks.EMBED_CHECKS:
            site_params['checks'].append(check(site_params))

        # Add the object itself
        return render(request, 'identity/embed.html', site_params)

    @staticmethod
    def get_embed_site_params(embed):
        site_params = cache.get(embed.derive_thirdparty_cache_path())

        if site_params is None:
            return None

        # TODO Add additional uncached metadata here
        try:
            # Check if we have an associated newsletter service
            assoc_service = Service.objects.get(url=embed.host)
            site_params["service"] = assoc_service
        except ObjectDoesNotExist:
            site_params["service"] = None

        return site_params


class EmbedMetaView(View):
    def post(self, request, *args, **kwargs):
        try:
            sid = request.POST['embedID']
            if str(sid) != str(kwargs['embed']):
                # Someone is messing with us
                logger.warn('EmbedMetaView.post: Provided embed did not match POSTed embed', extra={'request': request, "providedID": kwargs["embed"], "postID": sid})
                return redirect('Home')
            # Get service from database
            embed = Thirdparty.objects.get(id=sid)
        except KeyError:
            # No embed kwarg is set, warn
            logger.warn('EmbedMetaView.post: Malformed POST request received', extra={'request': request})
            # TODO: Add code to display a warning on homepage
            return redirect('Home')
        except ObjectDoesNotExist:
            logger.warn('EmbedMetaView.post: POST request for non-existing Thirdparty', extra={'request': request})
            return redirect('Home')

        form = forms.EmbedMetadataForm(request.POST)
        if not form.is_valid():
            logger.info('EmbedMetaView.post: Invalid data submitted on metadata form', extra={'request': request, 'form': form})
            return EmbedView.render(request, embed, form)

        # Form is valid
        sector = form.cleaned_data['sector']
        country = form.cleaned_data['country_of_origin']
        embed.country_of_origin = country
        embed.sector = sector
        embed.save()
        return redirect('Embed', embed=embed.id)


class FaqView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'faq.html')


class ImprintView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'imprint.html')


class PrivacyPolicyView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'privacy.html')
