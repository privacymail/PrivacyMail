import tldextract
from mailfetcher.models import Mail, Eresource
import hashlib

def import_openwpmresults_click(url, mail, db_cursor):
    num_eresources = 0
    num_eresources_dropped = 0
    # connect to the input database
    db_cursor.execute(
        "SELECT arguments from crawl_history where arguments LIKE ? AND command_status = 'ok' ;",
        ('%"url": "' + url + '"%',),
    )
    if len(db_cursor.fetchall()) == 0:
        return False
    # scans through the sqlite database, checking for all external calls and to which they redirect
    db_cursor.execute(
        "SELECT DISTINCT h.url, h.headers, hr.headers, h.top_level_url, r.new_request_url "
        "FROM site_visits as sv "
        "LEFT OUTER JOIN http_requests as h on h.visit_id = sv.visit_id "
        "LEFT OUTER JOIN http_redirects as r on h.url = r.old_request_url "
        "LEFT OUTER JOIN http_responses as hr on (h.request_id = hr.request_id and h.visit_id = hr.visit_id) "
        "WHERE h.url not like '%favicon.ico' and sv.site_url LIKE ?;",
        (url,),
    )

    openWPM_entries = db_cursor.fetchall()
    num_openWpm_entries = len(openWPM_entries)

    # check whether the final url is from the service. If not discard this chain.
    service_url = ""
    id = mail.identity.all()
    if id.exists():
        service_url = id[0].service.url
    else:
        print("Mail has no associated identities.")
        return True

    eresources_to_save = []
    drop_hosts = []

    for (
        url,
        request_headers,
        response_headers,
        top_url,
        redirects_to,
    ) in openWPM_entries:
        # check if the url has a parent and is therefore not the start of a chain.
        db_cursor.execute(
            "select * FROM http_redirects WHERE http_redirects.new_request_url = ?;",
            (url,),
        )

        is_start_of_chain = False
        if db_cursor.fetchone() is None:
            is_start_of_chain = True

        # eresource is end of chain
        if redirects_to is None or redirects_to == "":

            # If the last domain of a chain is not of our service, it was most likely an external link.
            # In many cases this would be unfair for the newsletter to track this as a thirdParty/ Tracker.
            url_domain = tldextract.extract(url).registered_domain
            service_url_tld = tldextract.extract(service_url).registered_domain
            if is_start_of_chain and (service_url_tld != url_domain):
                if url_domain not in drop_hosts:
                    drop_hosts.append(url)

            e = Eresource(
                type="con_click",
                request_headers=request_headers,
                response_headers=response_headers,
                url=url,
                channel_id=hashlib.md5(url.encode('utf-8')).hexdigest(),
                param=top_url,
                mail=mail,
                is_start_of_chain=is_start_of_chain,
                is_end_of_chain=True,
            )
            eresources_to_save.append(e)
        # eresource redirects to other eresource
        else:

            # If the last domain of a chain is not of our service, it was most likely an external link.
            # In many cases this would be unfair for the newsletter to track this as a thirdParty/ Tracker.
            #url_domain = tldextract.extract(url).registered_domain
            #service_url_tld = tldextract.extract(service_url).registered_domain
            #redirect_url_tld = tldextract.extract(redirects_to).registered_domain
            #if is_start_of_chain and (service_url_tld != url_domain) and (service_url_tld != redirect_url_tld):
            #    if url not in drop_hosts:
            #        drop_hosts.append(url)
            #        drop_hosts.append(redirects_to)
            #elif service_url_tld == redirect_url_tld:
            #    if url in drop_hosts:
            #        drop_hosts.remove(url)
            #    
            #    isStart = False
            #    while not isStart:
            #        foundOne = False
            #        for e in eresources_to_save:
            #            if e.redirects_to_url == url:
            #                foundOne = True
            #                drop_hosts.remove(url)
            #                if e.is_start_of_chain: 
            #                    isStart = True
            #        if not foundOne: isStart = True


            e = Eresource(
                type="con_click",
                request_headers=request_headers,
                response_headers=response_headers,
                url=url,
                channel_id=hashlib.md5(url.encode('utf-8')).hexdigest(),
                redirects_to_channel_id=hashlib.md5(url.encode('utf-8')).hexdigest(),
                redirects_to_url=redirects_to,
                param=top_url,
                mail=mail,
                is_start_of_chain=is_start_of_chain,
                is_end_of_chain=False,
            )
            eresources_to_save.append(e)

    # save load resources in eresource of type connection
    for e in eresources_to_save:
        isInList = False
        for drop_host in drop_hosts:
            if drop_host == e.url: isInList = True

        if not isInList:
            #print(e.url)
            e.save()
            mail.connect_tracker(eresource=e)
            e.save()
            num_eresources += +1
        else:
            print("Dropped:", e.url)
            num_eresources_dropped += 1
    print(
        "Added %s Eresources to the database (%s dropped)"
        % (num_eresources, num_eresources_dropped)
    )
    # if (num_openWpm_entries != num_eresources):
    #     print('Different number of entries have been added, than the OpenWPM database returned!')
    #     logger.error('Different number of entries have been added, than the OpenWPM database returned!')
    return True
