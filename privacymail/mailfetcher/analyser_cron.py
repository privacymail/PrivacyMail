from django_cron import CronJobBase, Schedule
from mailfetcher.models import Mail, Eresource, Service, Thirdparty
from identity.models import Identity, ServiceThirdPartyEmbeds
import statistics
import tldextract
import traceback
import logging
from django.core.cache import cache
from django.conf import settings
from datetime import datetime
from django.db.models import Q
import requests


logger = logging.getLogger(__name__)


def create_summary_cache(force=False):
    site_params = cache.get('result_summary')
    if site_params is not None and not force:
        if not site_params['cache_dirty']:
            return
    print('Building cache for summary')
    all_services = Service.objects.all()
    approved_services = all_services.filter(hasApprovedIdentity=True)
    num_approved_services = approved_services.count()
    services_using_cookies = 0
    services_with_address_disclosure = 0
    services_embedding_third_parties = 0
    for service in approved_services:
        third_party_connections = ServiceThirdPartyEmbeds.objects.filter(service=service)
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
        'num_services': all_services.count(),
        'num_approved_services': num_approved_services,
        # Num emails
        'num_received_mails': all_mails.count(),
        'percent_services_use_cookies': services_using_cookies / num_approved_services * 100,  # % of services set cookies. (on view and click?)
        'hosts_receiving_connections': num_hosts,  # Num third parties
        'percent_leak_address': services_with_address_disclosure / num_approved_services * 100,  # % of services leaking email address in any way
        'percent_embed_thirdparty': services_embedding_third_parties / num_approved_services * 100,  # % of services embed third parties
        'thirdparties_on_view': {  # third parties that are loaded by emails on view
            'min': -1,
            'max': -1,
            'median': -1,
            'mean': -1
        },
        'thirdparties_on_click': {  # third parties that are loaded by emails on click
            'min': -1,
            'max': -1,
            'median': -1,
            'mean': -1
        },
        'forwards_on_view': {  # forwards until reaching a resource per mail on view
            'min': -1,
            'max': -1,
            'median': -1,
            'mean': -1
        },
        'forwards_on_click': {  # forwards until reaching a resource per mail on click
            'min': -1,
            'max': -1,
            'median': -1,
            'mean': -1
        },
        'percent_personalised_urls': {  # % personalised urls per mail
            'min': -1,
            'max': -1,
            'median': -1,
            'mean': -1
        },
        'cache_dirty': False,
        'cache_timestamp': datetime.now().time()
    }
    # Cache the result
    cache.set('result_summary', site_params)


def create_third_party_cache(thirdparty, force=False):
    site_params = cache.get(thirdparty.derive_thirdparty_cache_path())
    if site_params is not None and not force:
        if not site_params['cache_dirty']:
            return
    print('Building cache for 3rd party: {}'.format(thirdparty.name))
    service_3p_conns = ServiceThirdPartyEmbeds.objects.filter(thirdparty=thirdparty)

    services = thirdparty.services.all()
    services = services.distinct()
    services_dict = {}
    for service in services:
        service_dict = {}
        embeds = service_3p_conns.filter(thirdparty=thirdparty)
        embeds_onview = embeds.filter(embed_type=ServiceThirdPartyEmbeds.ONVIEW)
        embeds_onclick = embeds.filter(embed_type=ServiceThirdPartyEmbeds.ONCLICK)
        # TODO check these
        service_dict['embed_as'] = list(embeds.values_list('embed_type', flat=True).distinct())
        service_dict['receives_address_view'] = embeds_onview.filter(leaks_address=True).exists()
        service_dict['receives_address_click'] = embeds_onclick.filter(leaks_address=True).exists()
        service_dict['sets_cookie'] = embeds.filter(sets_cookie=True).exists()
        service_dict['receives_identifiers'] = embeds.filter(receives_identifier=True).exists()

        services_dict[service] = service_dict

    receives_leaks = service_3p_conns.filter(leaks_address=True).exists()
    sets_cookies = service_3p_conns.filter(sets_cookie=True).exists()
    # Generate site params

    site_params = {
        'thirdparty': thirdparty,
        'used_by_num_services': services.count(),
        # How many services embed this third party
        'services': services_dict,
        # services_dict = {
        #     service:{
        #         embed_as: list{embedtypes}
            #     'address_leak_view': Bool
            #     'address_leak_click': Bool
            #     'sets_cookie': Bool
        #         'receives_identifiers': Bool
        #     }
        # }
        'receives_address': receives_leaks,  # done
        # 'leak_algorithms': [],  # TODO list of algorithms used to leak the address to this third party
        'sets_cookies': sets_cookies,
        'cache_dirty': False,
        'cache_timestamp': datetime.now().time()
    }
    # Cache the result
    cache.set(thirdparty.derive_thirdparty_cache_path(), site_params)


def create_service_cache(service, force=False):
    site_params = cache.get(service.derive_service_cache_path())

    if site_params is not None and not force:
        if not site_params['cache_dirty']:
            print('Cache exists and not dirty.')
            return
    print('Building cache for service: {}'.format(service.name))
    # logger.debug("ServiceView.render_service: Cache miss", extra={'request': request, 'service_id': service.id})
    # Get all identities associated with this service
    idents = Identity.objects.filter(service=service)
    # Count how many identities have received spam
    third_party_spam = idents.filter(receives_third_party_spam=True).count()
    # Get all mails associated with this domain
    mails = Mail.objects.filter(identity__in=idents, identity__approved=True).distinct()
    # Count these eMails
    count_mails = mails.count()
    # Count eMail that have pairs from another identity
    # TODO How does this deal with situations with more than two identities?
    count_mult_ident_mails = mails.exclude(mail_from_another_identity=None).count()

    # Get all ereseource
    # resources = Eresource.objects.filter(mail__in=mails)
    # Get links
    # links = service.avg('a')
    # ...and connections
    # connections = service.avg('con')
    # Get known trackers
    # tracker = Thirdparty.objects.filter(eresource__in=resources, eresource__type='con').distinct()
    # Check for eMails leakage
    mail_leakage_resources = Eresource.objects.filter(mail_leakage__isnull=False, mail__in=service.mails())
    algos_string = ""
    algos = []
    if mail_leakage_resources.exists():
        for algorithms_list in mail_leakage_resources.values_list('mail_leakage').distinct():
            for algorithm in algorithms_list[0].split(', '):
                if algorithm in algos or algorithm == '':
                    continue
                algos.append(algorithm)
        algos_string = ', '.join(algos)

    # Get all identities associated with this service
    idents = Identity.objects.filter(service=service, approved=True)
    # Create data structure for frontend

    # All identities of the service
    identities = Identity.objects.filter(service=service)
    emails = Mail.objects.filter(identity__in=identities, identity__approved=True).distinct()
    service_3p_conns = ServiceThirdPartyEmbeds.objects.filter(service=service)
    third_parties = service.thirdparties.all().distinct()

    cookies_per_mail = []
    for email in emails:
        cookies_per_mail.append(service_3p_conns.filter(mail=email, sets_cookie=True).count())
    try:
        cookies_set_mean = statistics.mean(cookies_per_mail)
    except:
        cookies_set_mean = 0

    third_parties_dict = {}

    counter_personalised_links = 0
    personalised_links = []
    personalised_anchor_links = []
    personalised_image_links = []
    num_embedded_links = []
    avg_personalised_image_links = 0
    avg_personalised_anchor_links = 0
    avg_num_embedded_links = 0
    ratio = 0
    for mail in service.mails():
        counter_personalised_links += 1
        all_static_eresources = Eresource.objects.filter(mail=mail). \
            filter(Q(type='a') | Q(type='link') | Q(type='img') | Q(type='script'))
        num_embedded_links.append(all_static_eresources.count())
        personalised_anchor_links.append(all_static_eresources.filter(type='a', personalised=True).count())
        personalised_image_links.append(all_static_eresources.filter(type='img', personalised=True).count())
        personalised_mails = all_static_eresources.filter(personalised=True)
        personalised_links.append(personalised_mails.count())
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
        third_party_dict = {}
        embeds = service_3p_conns.filter(thirdparty=third_party)
        embeds_onview = embeds.filter(embed_type=ServiceThirdPartyEmbeds.ONVIEW)
        embeds_onclick = embeds.filter(embed_type=ServiceThirdPartyEmbeds.ONCLICK)
        third_party_dict['embed_as'] = list(embeds.values_list('embed_type', flat=True).distinct())
        third_party_dict['address_leak_view'] = embeds_onview.filter(leaks_address=True).exists()
        third_party_dict['address_leak_click'] = embeds_onclick.filter(leaks_address=True).exists()
        third_party_dict['sets_cookie'] = embeds.filter(sets_cookie=True).exists()
        third_party_dict['receives_identifier'] = embeds.filter(receives_identifier=True).exists()
        third_parties_dict[third_party] = third_party_dict
    # static_links =
    # num_pairs, ratio, minimum, maximum, mean, median = analyze_differences_between_similar_mails(service)
    # Generate site params
    site_params = {
        # old params
        # 'idents': idents,
        # 'unconfirmed_idents': unconfirmed_idents,
        # 'resources': resources,
        # 'links': links,
        'count_mails': count_mails,
        'count_mult_ident_mails': count_mult_ident_mails,
        # 'connections': connections,
        # 'tracker': tracker,

        # new params
        # 'service': The service itself
        # 'idents': Queryset of identities of the service
        # 'count_mails': Number of emails received by the service
        # 'unconfirmed_idents': Queryset of unconfiremd identities
        # 'sets_cookies':  Bool: Uses cookies in any way (view and click).
        # 'leaks_address': Bool: Discloses email address in any way (view and click).
        'leak_algorithms': algos,
        'cookies_set_avg': cookies_set_mean,  # done
        # 'num_different_thirdparties': Number of different third parties
        # List different third parties, how embedded, address leak : done
        'third_parties': third_parties_dict,  # done
        # third_parties_dict = {
            # third_party: {
            #     'embed_as': list(embedtypes)
            #     'address_leak_view': Bool
            #     'address_leak_click': Bool
            #     'sets_cookie': Bool
            #     'receives_identifier': Bool }
        # Leaks email address to third party in any way : done
        'percent_links_personalised': ratio * 100,  # done
        'avg_personalised_anchor_links': avg_personalised_anchor_links,
        'avg_personalised_image_links': avg_personalised_image_links,
        'num_embedded_links': avg_num_embedded_links,
        # 'personalised_url': 'example.url',  # URL of with (longest) identifier
        # compare DOM-Tree of similar mails
        'suspected_AB_testing': emails.filter(possible_AB_testing=True).exists(),
        'third_party_spam': third_party_spam,  # Marked as receiving third party spam.
        'cache_dirty': False,
        'cache_timestamp': datetime.now().time(),
        # Information about the service itself is added by the wrapper loading the cache.
        # The service object will be available as site_params["service"].
    }
    # print ('AVG_ANCHOR: {}, AVG_IMAGE: {}, RATIO: {}, AVG_LINKS: {}'.format(avg_personalised_anchor_links, avg_personalised_image_links, ratio * 100, avg_num_embedded_links))
    # Cache the result
    cache.set(service.derive_service_cache_path(), site_params)


def analyse_dirty_services():
    dirty_services = Service.objects.filter(resultsdirty=True)
    for dirty_service in dirty_services:
        dirty_service.set_has_apprived_identity()
        print(dirty_service)
        analyze_differences_between_similar_mails(dirty_service)
        print('Differences Done')
        for mail in dirty_service.mails():
            mail.analyze_mail_connections_for_leakage()
            mail.create_service_third_party_connections()
        dirty_service.resultsdirty = False
        dirty_service.save()
        create_service_cache(dirty_service, True)


class Analyser(CronJobBase):
    RUN_EVERY_MINS = 2 * 60  # every 2 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'org.privacy-mail.analyser'    # a unique code

    # ser = Service.objects.get(pk=1)
    # tp = Thirdparty.objects.get(pk=1)
    # embedding = ServiceThirdPartyEmbeds.objects.create(
    #     service=ser, thirdparty=tp)

    def notify_webhook(self, case):
        if settings.CRON_WEBHOOKS:
            try:
                url = settings.CRON_WEBHOOKS['mailfetcher.analyser_cron.Analyser'][case]
                if url:
                    requests.get(url)
            except Exception:
                logger.warning("Analyser.notify_webhook: Failed to send signal.", exc_info=True)
                # No matter what happens here
                pass

    def do(self):

        try:
            self.notify_webhook('start')
            analyse_dirty_services()

            # Number of services that did not receive any mails.
            num_no_mails_received = 0
            identities_that_receive_mails = set()
            services_without_mails_set = set()
            for service in Service.objects.all():
                identities_that_receive_mails.add(service.name)
                if service.mails().count() == 0:
                    identities_that_receive_mails.remove(service.name)
                    num_no_mails_received += 1
                    services_without_mails_set.add(service)
            print('Services that did not receive mails: {}'.format(services_without_mails_set))
            all_mails = Mail.objects.all()
            print('A total of {} mails have been scanned.'.format(all_mails.count()))

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
                    e = Eresource.objects.filter(channel_id=url_chain[-1].redirects_to_channel_id)[0]
                    end_of_chain_reached = e.is_end_of_chain
                    url_chain.append(e)
                return url_chain

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
                    # eresource_set = eresource_set.exclude(url__contains=ext.domain)
                    # also not our local host
                    # eresource_set = eresource_set.exclude(url__contains=settings.LOCALHOST_URL)
                    # third_party_embeds = eresource_set.count()

                    for eresource in eresource_set:
                        resource_ext = tldextract.extract(eresource.url)
                        if service_ext.domain in resource_ext.domain or \
                                'privacymail.me' in (resource_ext.domain + '.' + resource_ext.suffix):
                            continue
                        third_party_domain = resource_ext.domain + '.' + resource_ext.suffix
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
                if service_ext.domain in resource_ext.domain or \
                        'privacymail.me' in (resource_ext.domain + '.' + resource_ext.suffix):
                    return False
                else:
                    return True

            # analyze one mail in more detail.
            def get_stats_of_mail(mail):
                num_third_parties_view = 0
                num_third_parties_static = 0
                print('Analyzing mail of service: {}'.format(mail.identity.all()[0].service))
                eresources_on_view = Eresource.objects.filter(mail=mail).filter(type='con')
                print('{} eresources loaded when viewing mail.'.format(eresources_on_view.count()))

                eresources_static = eresources_on_view.filter(is_start_of_chain=True)
                directly_embedded_third_party_count, directly_embedded_parties = \
                    third_parties_in_eresource_set(mail, eresources_static)
                print('{} links directly embedded ({} of them third party) in mail.'.
                      format(eresources_static.count(), directly_embedded_third_party_count))
                print('Third parties: {}'.format(directly_embedded_parties))

                additionaly_loaded_eresource_set = eresources_on_view.filter(is_start_of_chain=False)
                additionaly_loaded__third_party_count, additionaly_loaded_parties = \
                    third_parties_in_eresource_set(mail, additionaly_loaded_eresource_set)
                print('{} additional ones loaded through forwards ({} of them third party)'.
                      format(additionaly_loaded_eresource_set.count(), additionaly_loaded__third_party_count))
                print('Third parties: {}'.format(additionaly_loaded_parties))
                print('')

                leak_eresource_set = Eresource.objects.filter(mail=mail).filter(possible_unsub_link=False). \
                    exclude(mail_leakage__isnull=True)
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
                print('{} of included urls/websites (including first party, nondistinct) receive eMail address as'
                      ' hash, {} of them third party url and {} through forwards.'.
                      format(leak_eresource_set_count, num_of_leaks_to_third_parties,
                             num_of_leaks_through_forwards))
                print('The url chains, leaking the address via {}'.format(leaking_methods))
                for chain in chains:
                    for r in chain:
                        print(r.url)
                    print('')

                link_clicked_eresource_set = Eresource.objects.filter(mail=mail).filter(type='con_click')
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
                    print('{} urls are in the longest redirect chain that can be triggered by clicking a link'
                          .format(longest_chain_len))
                    for r in longest_chain:
                        print(r.url)
                print('End of mail analyzation')

            # get_stats_of_mail(Mail.objects.get(id=1899))

            def long_chains_calculation():
                print('The longest chains that leak the mailaddress when viewing:')
                # longest_chain = 0
                leak_chains = []
                for e in Eresource.objects.exclude(mail_leakage__isnull=True).exclude(possible_unsub_link=True) \
                        .filter(type='con').exclude(is_start_of_chain=False).exclude(is_end_of_chain=True). \
                        exclude(url__contains='examiner').exclude(url__contains='nbcnews'):  # \
                    # .exclude(url__icontains='examiner').exclude(url__icontains='nbcnews'):
                    chain = get_url_chain(e)

                    len_chain = len(chain)
                    if len_chain > 2:
                        # longest_chain = len_chain
                        leak_chains.append(chain)
                for chain in leak_chains:
                    r = chain[0]
                    identity = r.mail.identity.all()
                    if identity.count() > 0:
                        print('Service: {}, identity: {}, length: {}'.format(r.mail.identity.get().service,
                                                                             r.mail.identity.get(), len(chain)))
                        print('Mail Subject: {}'.format(r.mail.h_subject))
                        for url in chain:
                            print(url.url)
                        print('\n')

                print(
                    ' ########################## The longest chain for an embedded external resource.  ##########################')
                longest_chain = 0
                embed_chains = []
                for e in Eresource.objects.filter(mail_leakage__isnull=True).exclude(possible_unsub_link=True) \
                        .filter(type='con').exclude(is_start_of_chain=False).exclude(is_end_of_chain=True). \
                        exclude(url__contains='examiner').exclude(url__contains='nbcnews'):
                    chain = get_url_chain(e)

                    len_chain = len(chain)
                    if len_chain > 2:
                        longest_chain = len_chain
                        embed_chains.append(chain)
                # r = embed_chain[0]
                for chain in embed_chains:
                    r = chain[0]
                    identity = r.mail.identity.all()
                    if identity.count() > 0:
                        print('Service: {}, identity: {}, length: {}'.format(r.mail.identity.get().service,
                                                                             r.mail.identity.get(), len(chain)))
                        print('Mail Subject: {}'.format(r.mail.h_subject))
                        for url in chain:
                            print(url.url)
                        print('\n')
                # print('Service: {}, identity: {}, length: {}'.format(r.mail.identity.get().service,
                #                                                      r.mail.identity.get(), len(embed_chain)))
                # print('Mail Subject: {}'.format(r.mail.h_subject))
                # for url in embed_chains:
                #     print(url.url)
                # print('\n')

                print(
                    '##########################   The longest chain after clicking a link:   ##########################')
                longest_chain = 0
                click_chains = []
                for e in Eresource.objects.filter(type='con_click').exclude(possible_unsub_link=True) \
                        .exclude(is_start_of_chain=False).exclude(is_end_of_chain=True). \
                        exclude(url__contains='examiner').exclude(url__contains='nbcnews'):
                    chain = get_url_chain(e)

                    len_chain = len(chain)
                    if len_chain > 2:
                        longest_chain = len_chain
                        click_chains.append(chain)
                # r = click_chain[0]
                for chain in embed_chains:
                    r = chain[0]
                    identity = r.mail.identity.all()
                    if identity.count() > 0:
                        print('Service: {}, identity: {}, length: {}'.format(r.mail.identity.get().service,
                                                                             r.mail.identity.get(), len(chain)))
                        print('Mail Subject: {}'.format(r.mail.h_subject))
                        for url in chain:
                            print(url.url)
                        print('\n')
                # print('Service: {}, identity: {}, length: {}'.format(r.mail.identity.get().service,
                #                                                      r.mail.identity.get(), len(click_chain)))
                # print('Mail Subject: {}'.format(r.mail.h_subject))
                # for url in click_chain:
                #     print(url.url)
                # print('\n')

            # long_chains_calculation()

            def address_leakage_statistics():
                # Get the number of trackers that receive the mailaddress in plain or as hash
                leaking_resources = Eresource.objects.exclude(mail_leakage=None).exclude(possible_unsub_link=True)
                leaking_services = {}
                trackers = {}

                for r in leaking_resources:
                    # leaking_mails.append(r.mail)
                    leaking_algorithm = r.mail_leakage
                    if 'plainname' in leaking_algorithm:
                        leaking_algorithm = 'plain'
                    # record all identities that leak information and their algorithm
                    for id in r.mail.identity.all():
                        if id.service.name in leaking_services:
                            leaking_services[id.service.name].add(leaking_algorithm)
                        else:
                            leaking_services[id.service.name] = set()
                            leaking_services[id.service.name].add(leaking_algorithm)

                    # record all trackers and how they receive the address
                    if r.host.name in trackers:
                        trackers[r.host.name].add(leaking_algorithm)
                    else:
                        trackers[r.host.name] = set()
                        trackers[r.host.name].add(leaking_algorithm)
                print('{} different trackers (including the service itself) found,'
                      ' that receive the mailaddress in plain or as a hash.'
                      .format(len(trackers)))
                for tracker in trackers.keys():
                    print('{:<25} : {}'.format(tracker, trackers[tracker]))
                print('')

                # services = {}
                # for i in leaking_identities.keys:
                #     services.append(i.service.name)
                # services = list(set(services))
                num_all_services = Service.objects.all().count() - num_no_mails_received
                percent_of_services_leaking = round(len(leaking_services) / num_all_services * 100)
                print('{:.2f}% of services have links or connections, that leak the mailaddress in plain or '
                      'through a hash. ({} of total {})'
                      .format(percent_of_services_leaking, len(leaking_services), num_all_services))
                # print(leaking_services)
                for service in leaking_services.keys():
                    print('{:<25} : {}'.format(service, leaking_services[service]))
                print('\n')

            # address_leakage_statistics()

            def third_party_analization_general():
                service_by_third_party = {}  # third_party : number of services
                third_party_by_service = {}  # service : third parties

                for service in Service.objects.all():
                    third_parties_this_mail = {}
                    for mail in service.mails():
                        # check if we already have this service in our dict
                        if service.name not in third_party_by_service:
                            third_party_by_service[service.name] = set()

                        service_ext = tldextract.extract(service.url)
                        eresource_set = mail.eresource_set.filter(type='con')
                        # also not our local host
                        for eresource in eresource_set:
                            resource_ext = tldextract.extract(eresource.url)
                            third_party_domain = resource_ext.domain + '.' + resource_ext.suffix
                            if service_ext.domain in resource_ext.domain or \
                                    'privacymail.me' in third_party_domain:
                                continue
                            third_party_by_service[service.name].add(third_party_domain)
                            if third_party_domain in third_parties_this_mail:
                                third_parties_this_mail[third_party_domain] += 1
                            else:
                                third_parties_this_mail[third_party_domain] = 1
                    for third_party_domain in third_parties_this_mail.keys():
                        if third_party_domain in service_by_third_party:
                            service_by_third_party[third_party_domain] += 1
                        else:
                            service_by_third_party[third_party_domain] = 1

                print('Services that embed third parties without clicking links:')
                # Count, how many third parties each service uses.
                num_third_party_by_service = {}
                for service in third_party_by_service:
                    num_third_party_by_service[service] = len(third_party_by_service[service])
                s = [(k, num_third_party_by_service[k]) for k in sorted(num_third_party_by_service,
                                                                        key=num_third_party_by_service.get,
                                                                        reverse=True)]

                for k, v in s:
                    print('{:<25}: {:<5}: {}'.format(k, v, str(third_party_by_service[k])))
                # for service in third_party_by_service:
                #     print('{:<25}: {:<5}: {}'.format(service, len(third_party_by_service[service]), third_party_by_service[service]))

                third_party_by_service_clicked = {}  # service : third parties

                for service in Service.objects.all():
                    for mail in service.mails():
                        # check if we already have this service in our dict
                        if service.name not in third_party_by_service_clicked:
                            third_party_by_service_clicked[service.name] = set()
                        service_ext = tldextract.extract(service.url)
                        eresource_set = mail.eresource_set.filter(type__contains='con')
                        # also not our local host
                        for eresource in eresource_set:
                            resource_ext = tldextract.extract(eresource.url)
                            third_party_domain = resource_ext.domain + '.' + resource_ext.suffix
                            if service_ext.domain in resource_ext.domain or \
                                    'privacymail.me' in third_party_domain:
                                continue
                            third_party_by_service_clicked[service.name].add(third_party_domain)

                print('Services that embed third parties with clicking links:')
                # Count, how many third parties each service uses.
                num_third_party_by_service_clicked = {}
                for service in third_party_by_service:
                    num_third_party_by_service_clicked[service] = len(third_party_by_service_clicked[service])
                s = [(k, num_third_party_by_service_clicked[k])
                     for k in sorted(num_third_party_by_service_clicked, key=num_third_party_by_service_clicked.get,
                                     reverse=True)]
                for k, v in s:
                    print('{:<25}: {:<5}: {}'.format(k, v, str(third_party_by_service_clicked[k])))

                # How many % of mails embed third party resources?
                all_mails = Mail.objects.all()
                third_party_embeds = 0  # total embeds
                list_third_party_per_mail = []  # number of third parties per mail
                high = 0  # highest number of embeds per mail
                low = 50000  # lowest number of embeds per mail
                service_set_embedding_resources = set()
                # What kind of third parties
                third_party_count_per_mail = []
                third_parties = {}
                third_parties_min = 5000
                third_parties_max = 0
                for mail in all_mails:
                    third_parties_this_mail = {}
                    # identities of mail
                    id_of_mail = mail.identity.all()
                    if id_of_mail.count() > 0:
                        # all resources, that are pulled when viewing mail that don't contain the domain of the
                        # service in their url
                        service_ext = tldextract.extract(id_of_mail[0].service.url)
                        eresource_set = mail.eresource_set.filter(type='con')
                        # also not our local host
                        for eresource in eresource_set:
                            resource_ext = tldextract.extract(eresource.url)
                            third_party_domain = resource_ext.domain + '.' + resource_ext.suffix
                            if service_ext.domain in resource_ext.domain or \
                                    'privacymail.me' in third_party_domain:
                                continue

                            service_set_embedding_resources.add(id_of_mail[0].service)

                            if third_party_domain in third_parties_this_mail:
                                third_parties_this_mail[third_party_domain] += 1
                            else:
                                third_parties_this_mail[third_party_domain] = 1
                        for third_party_domain in third_parties_this_mail.keys():
                            if third_party_domain in third_parties:
                                third_parties[third_party_domain] += 1
                            else:
                                third_parties[third_party_domain] = 1
                        i = eresource_set.count()
                        list_third_party_per_mail.append(i)
                        if i > 0:
                            third_party_embeds = third_party_embeds + 1
                        if i > high:
                            high = i
                        if i < low:
                            low = i
                        third_parties_this_mail_count = len(third_parties_this_mail)
                        if third_parties_this_mail_count > third_parties_max:
                            third_parties_max = third_parties_this_mail_count
                        if third_parties_this_mail_count < third_parties_min:
                            third_parties_min = third_parties_this_mail_count
                        third_party_count_per_mail.append(third_parties_this_mail_count)
                percent_of_mail_embed = len(service_set_embedding_resources) / (Service.objects.all().count()
                                                                                - num_no_mails_received) * 100

                print('{:.2f}% of services have third party resources embedded. ({} of total {})'
                      .format(percent_of_mail_embed, len(service_set_embedding_resources),
                              Service.objects.all().count() - num_no_mails_received))

                print('{:.2f} third party resources on average per mail with a median of {}'.format(
                    statistics.mean(list_third_party_per_mail), statistics.median(list_third_party_per_mail)))
                print('Min. ext resources of a mail: {}'.format(low))
                print('Max. ext resources of a mail: {}\n'.format(high))

                print('{} different third parties found.'.format(len(third_parties)))
                print('#mails = Number of mails that try load the third party')
                print('usage = Number of services using the third party')
                print('{:<25} :{:<5}: {}'.format('####### Third Party', 'usage', '#mails ######'))

                s = [(k, service_by_third_party[k]) for k in sorted(service_by_third_party,
                                                                    key=service_by_third_party.get, reverse=True)]
                for k, v in s:
                    print('{:<25}: {:<5}: {}'.format(k, str(v), str(third_parties[k])))

                print('#########\n')
                print('{:.2f} third parties on average per mail with a median of {}'.format(
                    statistics.mean(third_party_count_per_mail), statistics.median(third_party_count_per_mail)))
                print('Min third parties in a mail: {}'.format(third_parties_min))
                print('Max third parties in a mail: {}'.format(third_parties_max))

            # third_party_analization_general()

            # mail_set = Mail.objects.filter(id=567)

            # analyze_differences_between_similar_mails()

            # all_resources = Eresource.objects.filter(url__contains='privacymail.me').delete()
            # all_mails = Mail.objects.all()
            # for e in all_resources:
            #     # print(e)
            #     e.delete()

            self.notify_webhook('success')
        except Exception as e:
            logger.error("AnalyserCron: Exception encoutered: %s" % e.__class__.__name__, exc_info=True)
            traceback.print_exc()
            self.notify_webhook('fail')


def analyze_differences_between_similar_mails(service):
    """
    Compares similar mails of a service.
    :param service: Which service to analyse.
    :return: num_pairs, ratio (personalised-/all links), minimum, maximum, mean, median
    """
    # counter = 0
    already_processed_mails = {}
    # mail_set = Mail.objects.all()
    mail_set = service.mails()
    # service_mail_metrics = {}
    pairs_analysed = 0
    diff_links_list = []
    total_num_links_list = []
    min_diff_list = []
    max_diff_list = []
    mean_diff_list = []
    median_diff_list = []
    ratio_list = []
    for m in mail_set:
        # TODO look for pairs instead of single mails, that have already been processed
        if m.id in already_processed_mails:
            continue

        already_processed_mails[m.id] = True
        identity = m.identity.all()
        if identity.count() > 0:
            identity = identity[0]
        else:
            logger.info('No associated identity with mail.', extra={'MailId': m.id})
            print('No associated identity with mail: {}'.format(m.id))
            continue
        # service = identity.service.name
        # results = {}
        # print(m)
        similar_mails = m.get_similar_mails_of_different_identities()
        if len(similar_mails) == 0:
            continue
        for el in similar_mails:
            if el.id in already_processed_mails:
                continue
            pairs_analysed += 1
            already_processed_mails[el.id] = True
            # print(el)
            difference_measure, differences = m.compare_text_of_mails(el)
            # print(difference_measure)
            # if difference_measure < 0.9993:
            if difference_measure < 0.985:
                logger.warning('Possible A/B testing', extra={'ID first mail': m.id, 'ID second mail': el.id,
                                                              'differences': differences})
                m.possible_AB_testing = True
                m.save()
                el.possible_AB_testing = True
                el.save()
                continue
                # print(differences)
            else:
                # print(m.get_similar_links(el))
                # m.get_similar_links(el)
                similar_links, num_diff_links, num_total_links, min_difference, max_difference, mean, median = \
                    m.get_similar_links(el, False)
                # if len(similar_links) == 0:
                #     continue
                try:
                    ratio_list.append(num_diff_links / num_total_links)
                except ZeroDivisionError:
                    ratio_list.append(0)
                diff_links_list.append(num_diff_links)
                total_num_links_list.append(num_total_links)
                min_diff_list.append(min_difference)
                max_diff_list.append(max_difference)
                mean_diff_list.append(mean)
                median_diff_list.append(median)
    if pairs_analysed == 0:
        return 0, -1, -1, -1, -1, -1
    try:
        ratio = statistics.mean(ratio_list)
        minimum = statistics.mean(min_diff_list)
        maximum = statistics.mean(max_diff_list)
        mean = statistics.mean(mean_diff_list)
        median = statistics.mean(median_diff_list)
        return pairs_analysed, ratio, minimum, maximum, mean, median
    except (statistics.StatisticsError, UnboundLocalError):
        return -1, -1, -1, -1, -1, -1

    # if counter % 50 == 0:
    #     print(counter)
    # counter += 1


def thesis_link_personalisation_of_services():
    # services = Service.objects.filter(hasApprovedIdentity=True)
    services = Service.objects.all()
    service_mail_metrics = {}

    # if service in service_mail_metrics:
    #     service_mail_metrics[service]['ratios'].append(num_diff_links / total_num_links)
    #     service_mail_metrics[service]['minimums'].append(min_difference)
    #     service_mail_metrics[service]['maximums'].append(max_difference)
    #     service_mail_metrics[service]['means'].append(mean)
    #     service_mail_metrics[service]['medians'].append(median)
    # else:
    #     service_mail_metrics[service] = {}
    #     service_mail_metrics[service]['ratios'] = [num_diff_links / total_num_links]
    #     service_mail_metrics[service]['minimums'] = [min_difference]
    #     service_mail_metrics[service]['maximums'] = [max_difference]
    #     service_mail_metrics[service]['medians'] = [median]
    #     service_mail_metrics[service]['means'] = [mean]

    print('Results of comparing links between similar mails of a service (per mail pair mean).')
    print('#pairs = number of total pairs compared')
    print('ratio =mean(number of different links/total number of links)')
    print('min = the mean minimum of different chars per different link')
    print('max = the mean maximum of different chars per different link')
    print('mean = the mean number of different chars per different link')
    print('median = the mean median of different chars per different link')
    print('{:<25}: {:<6}: {:<7}: {:<7}: {:<7}: {:<7}: {:<7}'.format('Service', '#pairs', 'ratio', 'min',
                                                                    'max', 'mean', 'median'))
    for service in services:
        service_name = service.name
        # if 'gruene.de' not in service.name:
        #     continue
        num_pairs, ratio, minimum, maximum, mean, median = analyze_differences_between_similar_mails(service)
        service_mail_metrics[service] = {}
        service_mail_metrics[service]['ratio'] = ratio
        service_mail_metrics[service]['minimum'] = minimum
        service_mail_metrics[service]['maximum'] = maximum
        service_mail_metrics[service]['median'] = median
        service_mail_metrics[service]['mean'] = mean
        print('{:<25}: {:<6}: {:<7.2f}: {:<7.2f}: {:<7.2f}: {:<7.2f}: {:<7.2f}'
              .format(service_name, num_pairs, ratio, minimum, maximum, mean, median))

        counter = 0
        personalised_links = []
        total_links = []
        for mail in service.mails():
            counter += 1
            all_static_eresources = Eresource.objects.filter(mail=mail).\
                filter(Q(type='a') | Q(type='link') | Q(type='img') | Q(type='script'))
            total_links.append(all_static_eresources.count())
            personalised_mails = all_static_eresources.filter(personalised=True)
            personalised_links.append(personalised_mails.count())
        if counter == 0:
            print('Continue')
            continue
        ratio = statistics.mean(personalised_links) / statistics.mean(total_links)
        print('Eresource Ratio: {}'.format(ratio))
