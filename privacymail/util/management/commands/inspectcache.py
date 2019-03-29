from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache
from identity.models import Service
import json


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('id', nargs='+', type=int)
        parser.add_argument('--service', action="store_true", dest="service", help="Show cache for specified service")

    def handle(self, *args, **options):
        if options['service']:
            for sid in options['id']:
                try:
                    service = Service.objects.get(pk=sid)
                    c = cache.get(service.derive_service_cache_path())
                    self.stdout.write(json.dumps(c))
                except Service.DoesNotExist:
                    raise CommandError('Service %s does not exist' % sid)
        else:
            raise CommandError("Must specify type of cache entry to look up (e.g. --service)")
