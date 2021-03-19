from django.conf import settings
from django.core.cache import cache
from identity.models import ServiceThirdPartyEmbeds
import tldextract


def get_stats_of_mail(service_url, eresources):
    stats = {}

    eresources_on_view = [
        eresource for eresource in eresources if eresource["type"] == "con"
    ]
    stats["eresources_on_view"] = len(eresources_on_view)
    eresources_static = [
        eresource for eresource in eresources_on_view if eresource["is_start_of_chain"]
    ]

    (
        _,
        directly_embedded_parties,
    ) = third_parties_in_single_mail(service_url, eresources_static)
    stats["directly_embedded_eresources"] = len(eresources_static)
    stats["directly_embedded_third_party"] = len(directly_embedded_parties)
    stats["third_parties"] =  []
    """
    for thirdparty in directly_embedded_parties:
        thirdpartyObject = ServiceThirdPartyEmbeds.objects.filter(thirdparty__name=thirdparty)
        if thirdpartyObject:
            stats["third_parties"].append(thirdpartyObject)
    """
    additionaly_loaded_eresource_set = [
        eresource for eresource in eresources_on_view if eresource["is_end_of_chain"]
    ]

    (
        additionaly_loaded__third_party_count,
        additionaly_loaded_parties,
    ) = third_parties_in_single_mail(service_url, additionaly_loaded_eresource_set)
    stats["additionaly_loaded_parties"] = len(additionaly_loaded_parties)
    stats[
        "additionaly_loaded__third_party_count"
    ] = additionaly_loaded__third_party_count
    stats["additionaly_loaded_parties"] = additionaly_loaded_parties

    leak_eresource_set = [
        eresource for eresource in eresources if "mail_leakage" in eresource
    ]
    leak_eresource_set_count = len(leak_eresource_set)

    num_of_leaks_to_third_parties = 0
    num_of_leaks_through_forwards = 0
    chains = []
    leaking_methods = []

    for r in leak_eresource_set:
        if is_third_party(service_url, r):
            num_of_leaks_to_third_parties += 1
        if not r["is_start_of_chain"]:
            num_of_leaks_through_forwards += 1
            chains.append(get_url_chain(r, eresources))
            if r["mail_leakage"] not in leaking_methods:
                leaking_methods.append(r["mail_leakage"])
    stats["leak_eresource_set_count"] = leak_eresource_set_count
    stats["num_of_leaks_to_third_parties"] = num_of_leaks_to_third_parties
    stats["num_of_leaks_through_forwards"] = num_of_leaks_through_forwards
    stats["leaking_methods"] = leaking_methods
    stats["leak_eresource_set"] = leak_eresource_set
    stats["chain"] = chains
    return stats


def get_url_chain(eresource, eresources):
    url_chain = []
    url_chain.append(eresource)

    # search for eresources in chain before given eresource
    start_of_chain_reached = eresource["is_start_of_chain"]
    while not start_of_chain_reached:
        redirected_eresources = [
            eresource
            for eresource in eresources
            if eresource["redirects_to_channel_id"]
        ]
        e = [
            eresource
            for eresource in redirected_eresources
            if eresource["redirects_to_channel_id"] == url_chain[0]["channel_id"]
        ][0]
        start_of_chain_reached = e["is_start_of_chain"]
        url_chain.insert(0, e)
    end_of_chain_reached = eresource["is_end_of_chain"]
    while not end_of_chain_reached:
        try:
            e = [
                eresource
                for eresource in eresources
                if eresource["channel_id"]
                and eresource["channel_id"] == url_chain[-1]["redirects_to_channel_id"]
            ][0]
            end_of_chain_reached = e["is_end_of_chain"]
            url_chain.append(e)
        # Should happen if the end of the chain has not been added, as it was a third party when clicking
        except:
            end_of_chain_reached = True
    return url_chain


def third_parties_in_single_mail(mail_url, eresource_set):
    third_party_embeds = 0  # total embeds
    # What kind of third parties
    third_parties = {}
    # identities of mail
    # all resources, that are pulled when viewing mail that don't contain the domain of the
    # service in their url
    service_ext = tldextract.extract(mail_url)
    for eresource in eresource_set:
        resource_ext = tldextract.extract(eresource["url"])
        if service_ext.domain in resource_ext.domain or "privacymail.info" in (
            resource_ext.domain + "." + resource_ext.suffix
        ):
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


def is_third_party(service_url, eresource):
    service_ext = tldextract.extract(service_url)
    resource_ext = tldextract.extract(eresource["url"])
    if not tldextract.extract(settings.LOCALHOST_URL).registered_domain:
        localdomain = "privacymail"
    else:
        localdomain = tldextract.extract(settings.LOCALHOST_URL).registered_domain

    if service_ext.domain in resource_ext.domain or localdomain in (resource_ext.domain + "." + resource_ext.suffix):
        return False
    else:
        return True


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