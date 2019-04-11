from django.views.generic import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from identity.util import validate_domain
from django.conf import settings
from identity.models import Identity, Service
from mailfetcher.analyser_cron import create_service_cache


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

            # Return the created identity
            r = JsonResponse({
                "site": url,
                "email": ident.mail,
                "first": ident.first_name,
                "last": ident.surname,
                "gender": "Male" if ident.gender else "Female"
            })
        except KeyError:
            print(request.POST)
            r = JsonResponse({"error": "No URL passed"})
        except AssertionError:
            # Invalid URL passed
            r = JsonResponse({"error": "Invalid URL passed."})
        r["Access-Control-Allow-Origin"] = "*"
        return r
