from django.core.management.base import BaseCommand
from django.core.cache import cache
from identity.models import Service
from mailfetcher.models import Thirdparty, Mail, Eresource
from mailfetcher import analyser_cron
from identity.views import ServiceView
import traceback

# This command was mainly used to call functions of the analyser cron for the thesis evaluation.
class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # cache.clear()
        # self.stdout.write('Cleared cache\n')

        # create_summary_cache(force=True)

        # wash = Service.objects.get(pk=1)
        # site_params = ServiceView.get_service_site_params(wash, force_makecache=True)
        # print(site_params)

        # for service in Service.objects.all():
        #     site_params = ServiceView.get_service_site_params(service, force_makecache=True)
        #     print(site_params)
        #     # create_service_cache(service, force=True)
        #
        # for thirdparty in Thirdparty.objects.all():
        #     create_third_party_cache(thirdparty, force=True)
        try:

            # analyser_cron.thesis_link_personalisation_of_services()
            # analyser_cron.any_connection_overview()
            analyser_cron.services_setting_cookies()
            # analyser_cron.any_connection_overview()
            # analyser_cron.third_party_analization_general()
            # analyser_cron.analyse_contacted_domains_from_cache()
            analyser_cron.address_leakage_statistics()
            # analyser_cron.long_chains_calculation()
            # analyser_cron.analyse_ab_testing()
            # analyser_cron.general_statistics()
            # analyser_cron.embedded_type_statistics()

        except Exception:
            traceback.print_exc()

        print('Done')
