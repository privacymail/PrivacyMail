from django_cron import CronJobBase, Schedule
from mailfetcher.models import Mail, Eresource, Thirdparty
from identity.models import Identity, ServiceThirdPartyEmbeds, Service
import statistics
import tldextract
import traceback
import logging
from multiprocessing import get_context, Pool, cpu_count
from django.core.cache import cache
from django.db import connections
from django.conf import settings
from datetime import datetime
from django.db.models import Q
from django import db
import requests
from mailfetcher.crons.mailCrawler.analysis.leakage import (
    analyze_mail_connections_for_leakage,
)

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
        print(service_information)
        third_parties_dict = service_information["third_parties_dict"]
        personalised_links = service_information["personalised_links"]
        personalised_anchor_links = service_information["personalised_anchor_links"]
        personalised_image_links = service_information["personalised_image_links"]
        num_embedded_links = service_information["num_embedded_links"]
        cookies_per_mail = service_information["cookies_per_mail"]
    else:
        third_parties_dict = {}
        personalised_links = []
        personalised_anchor_links = []
        personalised_image_links = []
        num_embedded_links = []
        cookies_per_mail = []

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
    # Count how many identities have received spam
    third_party_spam = idents.filter(receives_third_party_spam=True).count()
    # Get all mails associated with this domain
    mails = Mail.objects.filter(
        identity__in=idents, identity__approved=True
    ).distinct()  # Count these eMails
    count_mails = mails.count()
    # Count eMail that have pairs from another identity
    # TODO How does this deal with situations with more than two identities?
    count_mult_ident_mails = mails.exclude(mail_from_another_identity=None).count()

    mail_leakage_resources = Eresource.objects.filter(
        mail_leakage__isnull=False, mail__in=service.mails()
    )
    algos = []
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

    if not force:
        mails = service.mails_not_cached()

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
    if counter_personalised_links == 0:
        ratio = -1
    else:
        avg_num_embedded_links = statistics.mean(num_embedded_links)
        # TODO When does this happen?
        if avg_num_embedded_links == 0:
            ratio = 0
        else:
            ratio = statistics.mean(personalised_links) / avg_num_embedded_links
        avg_personalised_anchor_links = statistics.mean(personalised_anchor_links)
        avg_personalised_image_links = statistics.mean(personalised_image_links)

    for third_party in third_parties:
        if third_party not in third_parties_dict:
            create_third_party_cache(third_party, False)
            third_party_dict = {}
            embeds = service_3p_conns.filter(thirdparty=third_party)
            embeds_onview = embeds.filter(embed_type=ServiceThirdPartyEmbeds.ONVIEW)
            embeds_onclick = embeds.filter(embed_type=ServiceThirdPartyEmbeds.ONCLICK)
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
    service_information = {
        "personalised_links": personalised_links,
        "personalised_anchor_links": personalised_anchor_links,
        "personalised_image_links": personalised_image_links,
        "num_embedded_links": num_embedded_links,
        "third_parties_dict": third_parties_dict,
        "cookies_per_mail": cookies_per_mail,
    }
    # print ('AVG_ANCHOR: {}, AVG_IMAGE: {}, RATIO: {}, AVG_LINKS: {}'.format(avg_personalised_anchor_links, avg_personalised_image_links, ratio * 100, avg_num_embedded_links))
    # Cache the result
    cache.set(service.derive_service_cache_path(), site_params)
    cache.set(service.derive_service_information_cache(), service_information)


def analyse_dirty_services():
    # Re-generate caches for services with updated data
    dirty_services = Service.objects.filter(resultsdirty=True)
    print(dirty_services.count())
    if cpu_count() > 3:
        cpus = cpu_count() - 3
    else:
        cpus = 1
    with Pool(cpus) as p:
        p.map(analyse_dirty_service, dirty_services)


def analyse_dirty_service(dirty_service):
    connections.close_all()
    dirty_service.set_has_approved_identity()
    print(dirty_service)
    analyze_differences_between_similar_mails(dirty_service)
    dirty_service.resultsdirty = False
    dirty_service.save()
    create_service_cache(dirty_service, False)


def multiprocessing_create_service_cache(service):
    connections.close_all()
    create_service_cache(service, True)


class Analyser(CronJobBase):
    RUN_EVERY_MINS = 2 * 60  # every 2 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = "org.privacy-mail.analyser"  # a unique code

    # ser = Service.objects.get(pk=1)
    # tp = Thirdparty.objects.get(pk=1)
    # embedding = ServiceThirdPartyEmbeds.objects.create(
    #     service=ser, thirdparty=tp)

    def notify_webhook(self, case):
        if settings.CRON_WEBHOOKS:
            try:
                url = settings.CRON_WEBHOOKS["mailfetcher.analyser_cron.Analyser"][case]
                if url:
                    requests.get(url)
            except Exception:
                logger.warning(
                    "Analyser.notify_webhook: Failed to send signal.", exc_info=True
                )
                # No matter what happens here
                pass

    def do(self):

        try:
            # self.notify_webhook("start")
            analyse_dirty_services()

            # get_stats_of_mail(Mail.objects.get(id=1899))
            # address_leakage_statistics()

            self.notify_webhook("success")
        except Exception as e:
            logger.error(
                "AnalyserCron: Exception encoutered: %s" % e.__class__.__name__,
                exc_info=True,
            )
            traceback.print_exc()
            self.notify_webhook("fail")


# returns the number of third party resources in the set and a list of the third parties involved.
def third_parties_in_eresource_set(mail, eresource_set):
    third_party_embeds = 0  # total embeds
    # What kind of third parties
    third_parties = {}
    # identities of mail
    id_of_mail = mail.identity.all()
    if id_of_mail.count() > 0:
        # all resources, that are pulled when viewing mail that don't contain the domain of the
        # service in their url
        service_ext = tldextract.extract(id_of_mail[0].service.url)
        for eresource in eresource_set:
            resource_ext = tldextract.extract(eresource.url)
            if service_ext.domain in resource_ext.domain or tldextract.extract(
                settings.LOCALHOST_URL
            ).registered_domain in (resource_ext.domain + "." + resource_ext.suffix):
                continue
            third_party_domain = resource_ext.domain + "." + resource_ext.suffix
            third_party_embeds += 1
            if third_party_domain in third_parties:
                third_parties[third_party_domain] += 1
            else:
                third_parties[third_party_domain] = 1
    third_parties_list = []
    for third_party in third_parties.keys():
        third_parties_list.append(third_party)
    return third_party_embeds, third_parties_list


def is_third_party(identity, eresource):
    service_ext = tldextract.extract(identity.service.url)
    resource_ext = tldextract.extract(eresource.url)
    if service_ext.domain in resource_ext.domain or tldextract.extract(
        settings.LOCALHOST_URL
    ).registered_domain in (resource_ext.domain + "." + resource_ext.suffix):
        return False
    else:
        return True


# analyze one mail in more detail.
def get_stats_of_mail(mail):
    print("Analyzing mail of service: {}".format(mail.identity.all()[0].service))
    eresources_on_view = Eresource.objects.filter(mail=mail).filter(type="con")
    print("{} eresources loaded when viewing mail.".format(eresources_on_view.count()))

    eresources_static = eresources_on_view.filter(is_start_of_chain=True)
    (
        directly_embedded_third_party_count,
        directly_embedded_parties,
    ) = third_parties_in_eresource_set(mail, eresources_static)
    print(
        "{} links directly embedded ({} of them third party) in mail.".format(
            eresources_static.count(), directly_embedded_third_party_count
        )
    )
    print("Third parties: {}".format(directly_embedded_parties))

    additionaly_loaded_eresource_set = eresources_on_view.filter(
        is_start_of_chain=False
    )
    (
        additionaly_loaded__third_party_count,
        additionaly_loaded_parties,
    ) = third_parties_in_eresource_set(mail, additionaly_loaded_eresource_set)
    print(
        "{} additional ones loaded through forwards ({} of them third party)".format(
            additionaly_loaded_eresource_set.count(),
            additionaly_loaded__third_party_count,
        )
    )
    print("Third parties: {}".format(additionaly_loaded_parties))
    print("")

    leak_eresource_set = (
        Eresource.objects.filter(mail=mail)
        .filter(possible_unsub_link=False)
        .exclude(mail_leakage__isnull=True)
    )
    leak_eresource_set_count = leak_eresource_set.count()

    num_of_leaks_to_third_parties = 0
    num_of_leaks_through_forwards = 0
    ids_of_mail = mail.identity.all()
    chains = []
    leaking_methods = []
    if ids_of_mail.count() > 0:
        for r in leak_eresource_set:
            if is_third_party(ids_of_mail[0], r):
                num_of_leaks_to_third_parties += 1
            if not r.is_start_of_chain:
                num_of_leaks_through_forwards += 1
                chains.append(get_url_chain(r))
                leaking_methods.append(r.mail_leakage)
    print(
        "{} of included urls/websites (including first party, nondistinct) receive eMail address as"
        " hash, {} of them third party url and {} through forwards.".format(
            leak_eresource_set_count,
            num_of_leaks_to_third_parties,
            num_of_leaks_through_forwards,
        )
    )
    print("The url chains, leaking the address via {}".format(leaking_methods))
    for chain in chains:
        for r in chain:
            print(r.url)
        print("")

    link_clicked_eresource_set = Eresource.objects.filter(mail=mail).filter(
        type="con_click"
    )
    longest_chain_len = 0
    longest_chain = []
    if ids_of_mail.count() > 0:
        for r in link_clicked_eresource_set:
            if not is_third_party(ids_of_mail[0], r):
                continue
            chain = get_url_chain(r)
            if len(chain) > longest_chain_len:
                longest_chain_len = len(chain)
                longest_chain = chain
        print(
            "{} urls are in the longest redirect chain that can be triggered by clicking a link".format(
                longest_chain_len
            )
        )
        for r in longest_chain:
            print(r.url)
    print("End of mail analyzation")


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


def get_url_chain(eresource):
    url_chain = []
    url_chain.append(eresource)

    # search for eresources in chain before given eresource
    start_of_chain_reached = eresource.is_start_of_chain
    while not start_of_chain_reached:
        e = Eresource.objects.filter(redirects_to_channel_id=url_chain[0].channel_id)[0]
        start_of_chain_reached = e.is_start_of_chain
        url_chain.insert(0, e)
    end_of_chain_reached = eresource.is_end_of_chain
    while not end_of_chain_reached:
        try:
            e = Eresource.objects.filter(
                channel_id=url_chain[-1].redirects_to_channel_id
            )[0]
            end_of_chain_reached = e.is_end_of_chain
            url_chain.append(e)
        # Should happen if the end of the chain has not been added, as it was a third party when clicking
        except:
            end_of_chain_reached = True
    return url_chain
