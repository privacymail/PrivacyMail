from django.conf import settings
from ...models import Thirdparty
import tldextract


def get_stats_of_mail(service_url, eresources):
    stats = {}
    stats["third_parties"] =  []
    service_ext = tldextract.extract(service_url)
    stats["home_url"] = service_ext.domain + "." + service_ext.suffix
    stats["eresources"] = eresources
    eresources_on_view = [
        eresource for eresource in eresources if eresource["type"] == "con"
    ]
    for domain,eresource in third_parties_in_single_mail(eresources_on_view).items():
        third_party = {"name": domain, "url":domain}
        thirdpartyObject = Thirdparty.objects.filter(name=domain)
        if thirdpartyObject.count() > 0:
            third_party["sector"] = thirdpartyObject[0].sector
            third_party["host"] = thirdpartyObject[0].host
        else:
            third_party["sector"] = "unknown"
        if "mail_leakage" in eresource:
            third_party["address_leak_view"]: True
            third_party["receives_identifier"] = True
        else:
            third_party["address_leak_view"] = False
            third_party["receives_identifier"] = False
        stats["third_parties"].append(third_party)

    eresources_mail_leakage = [
        eresource for eresource in eresources if "mail_leakage" in eresource
    ]
    stats["mailLeakage"] = len(eresources_mail_leakage) > 0
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


def third_parties_in_single_mail( eresource_set):
    third_parties = {}

    for eresource in eresource_set:
        resource_ext = tldextract.extract(eresource["url"])
        third_party_domain = resource_ext.domain + "." + resource_ext.suffix
        if third_party_domain not in third_parties:
            third_parties[third_party_domain]= eresource
    return  third_parties


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