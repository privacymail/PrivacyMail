from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache
from identity.models import Service
from mailfetcher.models import Thirdparty
from pprint import pprint

from mailfetcher.analyser_cron import (
    analyse_dirty_service)

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('id', nargs='+', type=int)
        
    def handle(self, *args, **options):
        for sid in options['id']:
            try:
                service = Service.objects.get(pk=sid)
                analyse_dirty_service(service)
                c = cache.get(service.derive_service_cache_path())
                pprint(c)
            except Service.DoesNotExist:
                raise CommandError('Service %s does not exist' % sid)