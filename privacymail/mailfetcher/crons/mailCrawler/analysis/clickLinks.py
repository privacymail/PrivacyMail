from mailfetcher.models import Mail, Eresource
from django.conf import settings
import os
from OpenWPM.openwpm import CommandSequence, TaskManager
from django.db import connection, models

from mailfetcher.crons.mailCrawler.analysis.importClickResults import (
    import_openwpmresults_click,
)

import sqlite3 as lite


def call_openwpm_click_links(link_mail_map):
    # Click a specified link for a list of emails and save the results
    wpm_db = settings.OPENWPM_DATA_DIR + "crawl-data.sqlite"
    if os.path.exists(wpm_db):
        os.remove(wpm_db)

    print("Preparing data for OpenWPM.")
    sites = []
    for url in link_mail_map:
        sites.append(url)
    # The list of sites that we wish to crawl
    num_browsers = settings.NUMBER_OF_THREADS

    # Loads the manager preference and 3 copies of the default browser dictionaries
    print("Starting OpenWPM to visit links.")
    manager_params, browser_params = TaskManager.load_default_params(num_browsers)

    # Update browser configuration (use this for per-browser settings)
    for i in range(num_browsers):
        # Record HTTP Requests and Responses
        browser_params[i]["http_instrument"] = True
        # Enable flash for all three browsers
        # browser_params[i]['disable_flash'] = False
        # browser_params['js_instrument'] = True
        browser_params[i]["display_mode"] = "headless"
        browser_params[i]["prefs"] = {"browser.chrome.site_icons": False}

    # Update TaskManager configuration (use this for crawl-wide settings)
    manager_params["data_directory"] = settings.OPENWPM_DATA_DIR
    manager_params["log_directory"] = settings.OPENWPM_LOG_DIR

    # Instantiates the measurement platform
    # Commands time out by default after 60 seconds
    manager = TaskManager.TaskManager(manager_params, browser_params)

    # Visits the sites in succession rotating the browsers
    for site in sites:
        command_sequence = CommandSequence.CommandSequence(site, reset=True)

        # Start by visiting the page
        command_sequence.get(sleep=0, timeout=settings.OPENWPM_TIMEOUT)

        # Not dumping cookies here, as they can be extracted from the response headers
        # command_sequence.dump_profile_cookies(120)

        # index=None browsers visit sites asynchronously
        manager.execute_command_sequence(command_sequence, index=None)

    # Shuts down the browsers and waits for the data to finish logging
    manager.close()

    # Make sure the db connection is open
    connection.connect()

    print("Importing OpenWPM results.")
    failed_urls = {}
    wpm_db = settings.OPENWPM_DATA_DIR + "crawl-data.sqlite"

    if os.path.isfile(wpm_db):
        conn = lite.connect(wpm_db)
        db_cursor = conn.cursor()

        for url in link_mail_map:
            import_success = import_openwpmresults_click(
                url, link_mail_map[url], db_cursor
            )
            if not import_success:
                failed_urls[url] = link_mail_map[url]
                link_mail_map[url].processing_fails = (
                    link_mail_map[url].processing_fails + 1
                )
                link_mail_map[url].save()
            else:
                link_mail_map[
                    url
                ].processing_state = Mail.PROCESSING_STATES.LINK_CLICKED
                link_mail_map[url].processing_fails = 0
                link_mail_map[url].save()
        db_cursor.close()

        # remove openwpm sqlite db to avoid waste of disk space
        # if not settings.DEVELOP_ENVIRONMENT:
        #     os.remove(wpm_db)
    print("Done.")
    return failed_urls
