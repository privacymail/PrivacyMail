from django.core.management.base import BaseCommand
from django.core.cache import cache
from identity.models import Service
from mailfetcher.models import Thirdparty
from mailfetcher.analyser_cron import create_service_cache, create_summary_cache, create_third_party_cache
import time
import statistics
class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        print("Services")
        t = time.time()
        service1 = Service.objects.filter(id=1)[0]
        #print(service1.mails_not_cached().count()
        create_service_cache(service1, force=True)
        t2 = time.time()
        print(t2-t)
        print('Done')
