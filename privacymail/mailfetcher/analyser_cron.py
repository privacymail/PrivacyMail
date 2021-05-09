import requests
import statistics
import traceback
import logging
from datetime import datetime
from multiprocessing import get_context, Pool, cpu_count
from django_cron import CronJobBase, Schedule
from mailfetcher.models import Mail, Eresource, Thirdparty
from identity.models import Identity, ServiceThirdPartyEmbeds, Service
from django.core.cache import cache
from django.db import connections
from django.conf import settings
from django.db.models import Q
from django import db
from datetime import date
import time
import requests
from mailfetcher.crons.mailCrawler.analysis.leakage import (
    analyze_mail_connections_for_leakage,
)
from contextlib import closing

from identity.rating.rating import getAdjustedRating
logger = logging.getLogger(__name__)
LONG_SEPERATOR = "##########################################################"


def create_summary_cache(force=False):
    site_params = cache.get("result_summary")
    if site_params is not None and not force:
        if not site_params["cache_dirty"]:
            return
    print("Building cache for summary")
    all_services = Service.objects.all()
    approved_services = all_services.filter(hasApprovedIdentity=True)
    num_approved_services = approved_services.count()
    services_using_cookies = 0
    services_with_address_disclosure = 0
    services_embedding_third_parties = 0
    for service in approved_services:
        third_party_connections = ServiceThirdPartyEmbeds.objects.filter(
            service=service
        )
        if third_party_connections.filter(sets_cookie=True).exists():
            services_using_cookies += 1
        if third_party_connections.filter(leaks_address=True).exists():
            services_with_address_disclosure += 1
        tps = Thirdparty.objects.filter(name=service.url)
        if tps.exists():
            embeds = False
            for tp in tps:
                if third_party_connections.exclude(thirdparty=tp).exists():
                    embeds = True
            if embeds:
                services_embedding_third_parties += 1

    hosts = Thirdparty.objects.all()
    num_hosts = hosts.count()

    all_mails = Mail.objects.all()

    # Generate site params
    site_params = {
        # Num services (num services without approved identities)
        "num_services": all_services.count(),
        "num_approved_services": num_approved_services,
        # Num emails
        "num_received_mails": all_mails.count(),
        "percent_services_use_cookies": services_using_cookies
        / num_approved_services
        * 100,  # % of services set cookies. (on view and click?)
        "hosts_receiving_connections": num_hosts,  # Num third parties
        "percent_leak_address": services_with_address_disclosure
        / num_approved_services
        * 100,  # % of services leaking email address in any way
        "percent_embed_thirdparty": services_embedding_third_parties
        / num_approved_services
        * 100,  # % of services embed third parties
        "thirdparties_on_view": {  # third parties that are loaded by emails on view
            "min": -1,
            "max": -1,
            "median": -1,
            "mean": -1,
        },
        "thirdparties_on_click": {  # third parties that are loaded by emails on click
            "min": -1,
            "max": -1,
            "median": -1,
            "mean": -1,
        },
        "forwards_on_view": {  # forwards until reaching a resource per mail on view
            "min": -1,
            "max": -1,
            "median": -1,
            "mean": -1,
        },
        "forwards_on_click": {  # forwards until reaching a resource per mail on click
            "min": -1,
            "max": -1,
            "median": -1,
            "mean": -1,
        },
        "percent_personalised_urls": {  # % personalised urls per mail
            "min": -1,
            "max": -1,
            "median": -1,
            "mean": -1,
        },
        "cache_dirty": False,
        "cache_timestamp": datetime.now().time(),
    }
    # Cache the result
    cache.set("result_summary", site_params)


def create_third_party_cache(thirdparty, force=False):
    site_params = cache.get(thirdparty.derive_thirdparty_cache_path())
    if site_params is not None and not force:
        if not site_params["cache_dirty"]:
            return
    print("Building cache for 3rd party: {}".format(thirdparty.name))
    service_3p_conns = ServiceThirdPartyEmbeds.objects.filter(thirdparty=thirdparty)

    services = thirdparty.services.all()
    services = services.distinct()
    services_dict = {}
    for service in services:
        service_dict = {}
        embeds = service_3p_conns.filter(service=service)
        embeds_onview = embeds.filter(embed_type=ServiceThirdPartyEmbeds.ONVIEW)
        embeds_onclick = embeds.filter(embed_type=ServiceThirdPartyEmbeds.ONCLICK)
        # TODO check these
        service_dict["embed_as"] = list(
            embeds.values_list("embed_type", flat=True).distinct()
        )
        service_dict["receives_address_view"] = embeds_onview.filter(
            leaks_address=True
        ).exists()
        service_dict["receives_address_click"] = embeds_onclick.filter(
            leaks_address=True
        ).exists()
        service_dict["sets_cookie"] = embeds.filter(sets_cookie=True).exists()
        service_dict["receives_identifiers"] = embeds.filter(
            receives_identifier=True
        ).exists()

        services_dict[service] = service_dict

    receives_leaks = service_3p_conns.filter(leaks_address=True).exists()
    sets_cookies = service_3p_conns.filter(sets_cookie=True).exists()
    # Generate site params

    site_params = {
        "embed": thirdparty,
        "used_by_num_services": services.count(),
        "services": services_dict,
        "receives_address": receives_leaks,  # done
        "sets_cookies": sets_cookies,
        "cache_dirty": False,
        "cache_timestamp": datetime.now().time(),
    }
    # Cache the result
    cache.set(thirdparty.derive_thirdparty_cache_path(), site_params)


def create_service_cache(service, force=False):
    site_params = cache.get(service.derive_service_cache_path())
    service_information = cache.get(service.derive_service_information_cache())

    if service_information and not force:
        third_parties_dict = service_information["third_parties_dict"]
        personalised_links = service_information["personalised_links"]
        personalised_anchor_links = service_information["personalised_anchor_links"]
        personalised_image_links = service_information["personalised_image_links"]
        num_embedded_links = service_information["num_embedded_links"]
        cookies_per_mail = service_information["cookies_per_mail"]
        algos = service_information["algos"]
    else:
        third_parties_dict = {}
        personalised_links = []
        personalised_anchor_links = []
        personalised_image_links = []
        num_embedded_links = []
        cookies_per_mail = []
        algos = []

    counter_personalised_links = 0
    avg_personalised_image_links = 0
    avg_personalised_anchor_links = 0
    avg_num_embedded_links = 0
    ratio = 0
    # if site_params is not None and not force:
    #    if not site_params["cache_dirty"]:
    #        print("Cache exists and not dirty.")
    #        return

    print("Building cache for service: {}".format(service.name))
    # Get all identities associated with this service
    idents = Identity.objects.filter(service=service)
    if not force:
        mails = service.mails_not_cached()
    else:
        mails = Mail.objects.filter(
        identity__in=idents, identity__approved=True
        ).distinct()
    # Count how many identities have received spam
    third_party_spam = idents.filter(receives_third_party_spam=True).count()
    # Get all mails associated with this domain
    allmails = Mail.objects.filter(
        identity__in=idents, identity__approved=True
    ).distinct()  # Count these eMails
    count_mails = allmails.count()
    # Count eMail that have pairs from another identity
    # TODO How does this deal with situations with more than two identities?
    count_mult_ident_mails = allmails.exclude(mail_from_another_identity=None).count()
    print(mails.count())
    mail_leakage_resources = Eresource.objects.filter(
        mail_leakage__isnull=False, mail__in=mails
    )
    if mail_leakage_resources.exists():
        for algorithms_list in mail_leakage_resources.values_list(
            "mail_leakage"
        ).distinct():
            for algorithm in algorithms_list[0].split(", "):
                if algorithm in algos or algorithm == "":
                    continue
                algos.append(algorithm)

    service_3p_conns = ServiceThirdPartyEmbeds.objects.filter(service=service)
    third_parties = service.thirdparties.all().distinct()

    # Check if service has dead identities
    # Look for the 5th newest mail an identity has received
    for mail in mails:    
        cookies_per_mail.append(
            service_3p_conns.filter(mail=mail, sets_cookie=True).count()
        )
        counter_personalised_links += 1
        all_static_eresources = Eresource.objects.filter(mail=mail).filter(
            Q(type="a") | Q(type="link") | Q(type="img") | Q(type="script")
        )
        num_embedded_links.append(all_static_eresources.count())
        personalised_anchor_links.append(
            all_static_eresources.filter(type="a", personalised=True).count()
        )    
        personalised_image_links.append(
            all_static_eresources.filter(type="img", personalised=True).count()
        )
        personalised_mails = all_static_eresources.filter(personalised=True)
        personalised_links.append(personalised_mails.count())
        mail.cached = True
        mail.save()

    try:
        cookies_set_mean = statistics.mean(cookies_per_mail)
    except:
        cookies_set_mean = 0
    try:
        avg_num_embedded_links = statistics.mean(num_embedded_links)
    except:
        avg_num_embedded_links = 0
    # TODO When does this happen?
    if avg_num_embedded_links == 0:
        ratio = 0
    else:
        ratio = statistics.mean(personalised_links) / avg_num_embedded_links        
    try:
        avg_personalised_anchor_links = statistics.mean(personalised_anchor_links)
    except:
        avg_personalised_anchor_links = 0
    try:
        avg_personalised_image_links = statistics.mean(personalised_image_links)
    except:
        avg_personalised_image_links = 0

    for third_party in third_parties:
        if third_party not in third_parties_dict:
            #create_third_party_cache(third_party, False)
            third_party_dict = {}
            embeds = service_3p_conns.filter(thirdparty=third_party)
            embeds_onview = embeds.filter(embed_type=ServiceThirdPartyEmbeds.ONVIEW)
            embeds_onclick = embeds.filter(embed_type=ServiceThirdPartyEmbeds.ONCLICK)

            third_party_dict["last_seen"] = embeds.order_by("-mail__date_time").first().mail.date_time

            #Now check for the relevant timeframe
            third_party_dict["embed_as"] = list(
                embeds.values_list("embed_type", flat=True).distinct()
            )
            third_party_dict["address_leak_view"] = embeds_onview.filter(
                leaks_address=True
            ).exists()
            third_party_dict["address_leak_click"] = embeds_onclick.filter(
                leaks_address=True
            ).exists()
            third_party_dict["sets_cookie"] = embeds.filter(sets_cookie=True).exists()
            third_party_dict["receives_identifier"] = embeds.filter(
                receives_identifier=True
            ).exists()


            third_parties_dict[third_party] = third_party_dict

    site_params = {
        "count_mails": count_mails,
        "count_mult_ident_mails": count_mult_ident_mails,
        "leak_algorithms": algos,
        "cookies_set_avg": cookies_set_mean,  # done
        "third_parties": third_parties_dict,  # done
        "percent_links_personalised": ratio * 100,  # done
        "avg_personalised_anchor_links": avg_personalised_anchor_links,
        "avg_personalised_image_links": avg_personalised_image_links,
        "num_embedded_links": avg_num_embedded_links,
        "suspected_AB_testing": mails.filter(possible_AB_testing=True).exists(),
        "third_party_spam": third_party_spam,  # Marked as receiving third party spam.
        "cache_dirty": False,
        "cache_timestamp": datetime.now().time(),
    }
    site_params["rating"] = getAdjustedRating(service)
    service_information = {
        "personalised_links": personalised_links,
        "personalised_anchor_links": personalised_anchor_links,
        "personalised_image_links": personalised_image_links,
        "num_embedded_links": num_embedded_links,
        "third_parties_dict": third_parties_dict,
        "cookies_per_mail": cookies_per_mail,
        "algos": algos
    }
    # print ('AVG_ANCHOR: {}, AVG_IMAGE: {}, RATIO: {}, AVG_LINKS: {}'.format(avg_personalised_anchor_links, avg_personalised_image_links, ratio * 100, avg_num_embedded_links))
    # Cache the result
    cache.set(service.derive_service_cache_path(), site_params)
    cache.set(service.derive_service_information_cache(), service_information)


def analyse_dirty_services():
    # Re-generate caches for services with updated data
    dirty_services = Service.objects.filter(resultsdirty=True)
    print(dirty_services.count())
    if cpu_count() > 5:
        cpus = cpu_count() - 5
    else:
        cpus = 1

    with closing(Pool(cpus,maxtasksperchild=1)) as p:
        p.map(analyse_dirty_service, dirty_services)


def analyse_dirty_service(dirty_service):
    connections.close_all()
    dirty_service.set_has_approved_identity()
    print(dirty_service)
    mark_idents_as_dead(dirty_service)
    analyze_differences_between_similar_mails(dirty_service)
    dirty_service.resultsdirty = False
    dirty_service.save()
    create_service_cache(dirty_service, False)


def multiprocessing_create_service_cache(service):
    connections.close_all()
    now = time.time()
    create_service_cache(service, True)
    print(f"Service creation for {service.name} took : {time.time() - now }")
    

def multiprocessing_create_thirdparty_cache(thirdparty):
    connections.close_all()
    create_third_party_cache(thirdparty, True)

class Analyser(CronJobBase):
    RUN_EVERY_MINS = 2 * 60  # every 2 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = "org.privacy-mail.analyser"  # a unique code

    # ser = Service.objects.get(pk=1)
    # tp = Thirdparty.objects.get(pk=1)
    # embedding = ServiceThirdPartyEmbeds.objects.create(
    #     service=ser, thirdparty=tp)
    def do(self):

        try:
            analyse_dirty_services()

            # get_stats_of_mail(Mail.objects.get(id=1899))
            # address_leakage_statistics()

        except Exception as e:
            logger.error(
                "AnalyserCron: Exception encoutered: %s" % e.__class__.__name__,
                exc_info=True,
            )
            traceback.print_exc()


# analyze one mail in more detail.
def analyze_differences_between_similar_mails(service):
    """
    Compares similar mails of a service.
    :param service: Which service to analyse.
    :return: num_pairs, ratio (personalised-/all links), minimum, maximum, mean, median
    """
    # counter = 0
    already_processed_mails = {}
    # mail_set = Mail.objects.all()
    mail_set = service.mails_similarity_not_processed()
    # service_mail_metrics = {}
    pairs_analysed = 0
    for m in mail_set:
        # TODO look for pairs instead of single mails, that have already been processed
        if m.id in already_processed_mails:
            continue
        already_processed_mails[m.id] = True
        m.similarity_processed = True
        m.save()
        identity = m.identity.all()
        if identity.count() > 0:
            identity = identity[0]
        else:
            logger.info("No associated identity with mail.", extra={"MailId": m.id})
            print("No associated identity with mail: {}".format(m.id))
            continue
        # service = identity.service.name
        # results = {}
        # print(m)
        similar_mails = m.get_similar_mails_of_different_identities()
        if len(similar_mails) == 0:
            continue
        for el in similar_mails:
            # if el.id in already_processed_mails:
            #     continue
            pairs_analysed += 1
            already_processed_mails[el.id] = True
            # print(el)
            difference_measure, _ = m.compare_text_of_mails(el)
            # print(difference_measure)
            # if difference_measure < 0.9993:
            if difference_measure < 0.985:
                # logger.warning('Possible A/B testing', extra={'ID first mail': m.id, 'ID second mail': el.id,
                #                                               'differences': differences})
                m.possible_AB_testing = True
                m.save()
                el.possible_AB_testing = True
                el.save()
                continue
            else:
                m.get_similar_links(el)

def mark_idents_as_dead(service): 

    idents = Identity.objects.filter(service=service)
    last_5_mail_date = date.min;

    for identity in idents: 
        identity_mails = Mail.objects.filter(
            identity=identity
        ).distinct().order_by("-date_time")

        if len(identity_mails) >= 5:
            date_time = identity_mails[4].date_time.date()

            if date_time > last_5_mail_date:
                last_5_mail_date = date_time
        
    for identity in idents: 
        identity_mails = Mail.objects.filter(
            identity=identity
        ).distinct().order_by("-date_time")

        if len(identity_mails) > 0:
            last_mail_date = identity_mails.first().date_time.date()

            if last_mail_date < last_5_mail_date: 
                identity.mark_as_dead()
            else : 
                identity.resurrect()
