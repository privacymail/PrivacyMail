from mailfetcher.models import Mail, Eresource
import hashlib


def import_openwpmresults(filename, mail, db_cursor):
    # Import the results from the OpenWPM sqlite database and write it to the backend database of Django
    num_eresources = 0
    # Checks if the the command got executed successfully
    db_cursor.execute(
        "SELECT arguments from crawl_history where arguments LIKE ? AND command_status = 'ok' ;",
        ('%"url": "' + filename + '"%',),
    )
    if len(db_cursor.fetchall()) == 0:
        return False
    # scans through the sqlite database, checking for all external calls and to which they redirect
    db_cursor.execute(
        "SELECT DISTINCT h.url, h.headers, hr.headers, h.top_level_url, r.new_request_url "
        "FROM http_requests as h "
        "LEFT OUTER JOIN http_redirects as r on h.url = r.old_request_url "
        "LEFT OUTER JOIN http_responses as hr on (h.request_id = hr.request_id and h.visit_id = hr.visit_id) "
        "WHERE h.url not like '%favicon.ico' and h.url not like ? and h.top_level_url LIKE ?;",
        (filename, filename),
    )

    openWPM_entries = db_cursor.fetchall()
    num_openWpm_entries = len(openWPM_entries)
    # scans through the database, checking for all external calls
    # for url, top_url in cur.execute("SELECT DISTINCT h.url, v.site_url "
    #                                 "FROM http_requests as h JOIN site_visits as v ON "
    #                                 "h.visit_id = v.visit_id WHERE top_level_url = ?;", (filename,)):
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
            r, created = Eresource.objects.get_or_create(
                type="con",
                request_headers=request_headers,
                response_headers=response_headers,
                url=url,
                channel_id=hashlib.md5(url.encode("utf-8")).hexdigest(),
                param=top_url,
                mail=mail,
                is_start_of_chain=is_start_of_chain,
                is_end_of_chain=True,
            )
        # eresource redirects to other eresource
        else:
            r, created = Eresource.objects.get_or_create(
                type="con",
                request_headers=request_headers,
                response_headers=response_headers,
                url=url,
                channel_id=hashlib.md5(url.encode("utf-8")).hexdigest(),
                redirects_to_channel_id=hashlib.md5(
                    redirects_to.encode("utf-8")
                ).hexdigest(),
                redirects_to_url=redirects_to,
                param=top_url,
                mail=mail,
                is_start_of_chain=is_start_of_chain,
                is_end_of_chain=False,
            )

        # save load resources in eresource of type connection
        if created:
            mail.connect_tracker(eresource=r)
            r.save()
            num_eresources = num_eresources + 1
    print("Number of Eresources added to the Database: %s" % num_eresources)

    if num_openWpm_entries != num_eresources:
        print(
            "Different number of entries have been added, than the OpenWPM database returned! Should have written %s"
            % num_openWpm_entries
        )
    return True
