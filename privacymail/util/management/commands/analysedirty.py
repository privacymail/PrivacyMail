from django.core.management.base import BaseCommand
from django.core.cache import cache
from identity.models import Service
from mailfetcher.models import Thirdparty
import multiprocessing
from itertools import repeat
from mailfetcher.analyser_cron import (
    create_service_cache,
    create_summary_cache,
    create_third_party_cache,
    analyse_dirty_services,
    multiprocessing_create_service_cache,
)
from django.db import connections


class Command(BaseCommand):
    def handle(self, *args, **kwargs):

        cache.clear()
        self.stdout.write("Analysing dirty Services\n")

        # create_summary_cache(force=True)
        
        analyse_dirty_services()

        print("Done")
