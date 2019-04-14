from django.core.management.base import BaseCommand
from django.core.cache import cache
from identity.models import Service
from mailfetcher.models import Thirdparty, Mail, Eresource
from mailfetcher import analyser_cron
from identity.views import ServiceView
import traceback


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
            services_without_pairs_found = "['docmorris.de', 'spd.de', 'kuechenstud.io', 'vinocentral.de', 'bahn.de', 'fastcompany.com', 'phoenix.de', 'cinemaxx.de', 'kinopolis.de', 'ballverliebt.eu', 'suedkurier.de', 'naturfreunde.de', 'lidl.de', 'engelhorn.de', 'ghacks.net', 'bonprix.de', 'thinkster.io']"
            analyser_cron.thesis_link_personalisation_of_services_only_eresources(services_without_pairs_found)
            # analyser_cron.third_party_analization_general()
            # analyser_cron.analyse_contacted_domains_from_cache()
            # analyser_cron.address_leakage_statistics()
            # analyser_cron.long_chains_calculation()
            # analyser_cron.analyse_ab_testing()
            # hm_service = Service.objects.get(name='hm.com')
            # analyser_cron.analyze_differences_between_similar_mails(hm_service)
            # analyser_cron.general_statistics()

        except Exception:
            traceback.print_exc()

        print('Done')
