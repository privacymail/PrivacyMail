from django.core.management.base import BaseCommand
from django.core.cache import cache
from identity.models import Service
from mailfetcher.models import Thirdparty
from mailfetcher.analyser_cron import create_service_cache, create_summary_cache, create_third_party_cache


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        cache.clear()
        self.stdout.write('Cleared cache\n')

        create_summary_cache(force=True)

        for service in Service.objects.all():
            create_service_cache(service, force=True)

        for thirdparty in Thirdparty.objects.all():
            create_third_party_cache(thirdparty, force=True)

        print('Done')
