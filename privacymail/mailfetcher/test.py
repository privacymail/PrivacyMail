import os
import sqlite3 as lite
from django.db import connection

def import_openwpmresults(filename,  db_cursor):
    # Import the results from the OpenWPM sqlite database and write it to the backend database of Django
    num_eresources = 0

    print("Importing ", filename, (filename,))
    #Checks if the the command got executed successfully
    db_cursor.execute(
        #"SELECT * from crawl_history;", #TODO the old statement wouldnt work. this needs to be fixed --> 
        #"SELECT arguments from crawl_history where arguments LIKE ? ;",
        #('%"url": %',)
        "SELECT arguments from crawl_history where arguments LIKE ? ;",
        ('%"url": "'+filename+'"%',)
    )
   
    if len(db_cursor.fetchall()) == 0:
        print("no files found")
        return False
    # scans through the sqlite database, checking for all external calls and to which they redirect
    db_cursor.execute(
        "SELECT DISTINCT h.url, h.headers, hr.headers, h.request_id, v.site_url, r.new_request_id, h2.url "
        "FROM http_requests as h INNER JOIN site_visits as v on h.visit_id = v.visit_id "
        "LEFT OUTER JOIN http_redirects as r on h.request_id = r.old_request_id "
        "LEFT OUTER JOIN http_requests as h2 on r.new_request_id = h2.request_id "
        "LEFT OUTER JOIN http_responses as hr on h.url = hr.url "
        "WHERE h.url not like '%favicon.ico' and site_url = ?;",
        (filename,),
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
        channel_id,
        top_url,
        new_channel_id,
        redirects_to,
    ) in openWPM_entries:
        # check if the url has a parent and is therefore not the start of a chain.
        db_cursor.execute(
            "select * FROM http_redirects WHERE http_redirects.new_request_id = ?;",
            (channel_id,),
        )

        is_start_of_chain = False
        if db_cursor.fetchone() is None:
            is_start_of_chain = True

        # eresource is end of chain
        if new_channel_id is None or new_channel_id == "":
            r, created = Eresource.objects.get_or_create(
                type="con",
                request_headers=request_headers,
                response_headers=response_headers,
                url=url,
                channel_id=channel_id,
                param=top_url,
                #mail=mail,
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
                channel_id=channel_id,
                redirects_to_channel_id=new_channel_id,
                redirects_to_url=redirects_to,
                param=top_url,
                mail=mail,
                is_start_of_chain=is_start_of_chain,
                is_end_of_chain=False,
            )

        # save load resources in eresource of type connection
        if created:
            #mail.connect_tracker(eresource=r)
            r.save()
            num_eresources = num_eresources + 1
    print("Number of Eresources added to the Database: %s" % num_eresources)
    if num_openWpm_entries != num_eresources:
        print(
            "Different number of entries have been added, than the OpenWPM database returned!"
        )
    return True



print("Importing OpenWPM results.")
failed_mails = []
mailFiles = ["http://localhost:5000/tmp_7ar9292.html"]

wpm_db =  "/home/privacymail/privacymailData/data/crawl-data.sqlite"
if os.path.isfile(wpm_db):
    conn = lite.connect(wpm_db)
    conn.set_trace_callback(print)
    db_cursor = conn.cursor()

    for fileName in mailFiles:
        successful_import = import_openwpmresults(fileName, db_cursor)
        if not successful_import:
            failed_mails.append(file_to_mail_map[fileName])
            file_to_mail_map[fileName].processing_fails = (
                file_to_mail_map[fileName].processing_fails + 1
            )
            file_to_mail_map[fileName].save()
        else:
            file_to_mail_map[
                fileName
            ].processing_state = Mail.PROCESSING_STATES.VIEWED
            file_to_mail_map[fileName].processing_fails = 0
            file_to_mail_map[fileName].save()
        os.unlink('/tmp/' + fileName.split('/')[3])  # remove file to avoid zombie data
    db_cursor.close()

    # remove openwpm sqlite db to avoid waste of disk space
    if not settings.DEVELOP_ENVIRONMENT:
        os.remove(wpm_db)
print("Done.")



