from django.views.generic import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from identity.util import validate_domain
from django.conf import settings
from identity.models import Identity, Service
from mailfetcher.analyser_cron import create_service_cache
import logging
from random import shuffle

logger = logging.getLogger(__name__)


class BookmarkletApiView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(BookmarkletApiView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            url = request.POST["url"]
            url = validate_domain(url)

            # Get or create the service matching this domain
            service, created = Service.get_or_create(url=url, name=url)
            service.save()

            # Select a domain to use for the identity
            # Create a list of possible domains
            domains = [cred["DOMAIN"] for cred in settings.MAILCREDENTIALS]
            # Shuffle it
            shuffle(domains)
            # Iterate through it
            for identityDomain in domains:
                # If the domain has not yet been used, stop the loop, otherwise try the next
                if Identity.objects.filter(service_id=service.pk).filter(mail__contains=identityDomain).count() == 0:
                    break
            # At this point, we have either selected a domain that has not yet been used for the
            # provided service, or the service already has at least one identity for each domain,
            # in which case we have picked one domain at random (by shuffling the list first).

            # Create an identity and save it
            ident = Identity.create(service, identityDomain)
            ident.save()

            if created:
                create_service_cache(service, force=True)

            # Return the created identity
            r = JsonResponse({
                "site": url,
                "email": ident.mail,
                "first": ident.first_name,
                "last": ident.surname,
                "gender": "Male" if ident.gender else "Female"
            })
        except KeyError:
            logger.warning("BookmarkletApiView.post: Malformed request received, missing url.", extra={'request': request})
            r = JsonResponse({"error": "No URL passed"})
        except AssertionError:
            # Invalid URL passed
            logger.warning("BookmarkletApiView.post: Malformed request received, malformed URL.", extra={'request': request})
            r = JsonResponse({"error": "Invalid URL passed."})
        r["Access-Control-Allow-Origin"] = "*"
        return r
