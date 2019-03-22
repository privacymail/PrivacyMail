from django.core.management.base import BaseCommand
from django.core.cache import cache
from identity.models import Service
from mailfetcher.models import Thirdparty
from mailfetcher.analyser_cron import create_service_cache, create_summary_cache, create_third_party_cache
from multiprocessing import cpu_count, Pool
from functools import partial


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        cache.clear()
        self.stdout.write('Cleared cache\n')

        create_summary_cache(force=True)

        # Create multiprocessing pool, using 3/4th of available CPUs
        # (leave a few CPUs available for handling other tasks)
        pool = Pool(processes=int(cpu_count() / 4 * 3))

        # Prepare service cache partial function
        csc = partial(create_service_cache, force=True)
        # Call in parallel
        pool.map(csc, Service.objects.all())

        # Prepare third party service cache partial function
        ctpc = partial(create_third_party_cache, force=True)
        # Call in parallel
        pool.map(ctpc, Thirdparty.objects.all())

        # Wait for tasks to terminate
        pool.join()
        print('Done')
