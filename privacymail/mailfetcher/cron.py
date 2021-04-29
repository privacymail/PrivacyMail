import logging
import poplib

from django.conf import settings
from django_cron import CronJobBase, Schedule

from mailfetcher.crons.mailCrawler.init import init
from mailfetcher.crons.mailCrawler.getUnfinishedMailCount import getUnfinishedMailCount
from mailfetcher.crons.mailCrawler.openWPM import (
    analyzeOnView,
    analyzeOnClick,
    analyzeLeaks,
    kill_openwpm,
)
from mailfetcher.crons.mailCrawler.fetchMails import fetchMails

import time

poplib._MAXLINE = 20480
logger = logging.getLogger(__name__)


class ImapFetcher(CronJobBase):
    RUN_EVERY_MINS = 5

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = "org.privacy-mail.imapfetcher"  # a unique code

    def do(self):
        # Work around a bug with the caching library

        # Start measuring the time from the beginning.
        start_time = time.time()
        server, thread = init()

        mails_left = True
        # Continue until all mails processed.
        while mails_left:
            unfinished_mail_count = getUnfinishedMailCount()
            # Have at most settings.CRON_MAILQUEUE_SIZE messages in the queue. If we have less than that,
            # retrieve new messages from the mail server
            if unfinished_mail_count >= settings.CRON_MAILQUEUE_SIZE:
                print(
                    "Too many unfinished mails in database. Continuing without fetching new ones."
                )
            else:
                mails_left = fetchMails(unfinished_mail_count)

            # Run OpenWPM; View the Mail, then visit one of it's links.
            analyzeOnView()

            analyzeOnClick()

            analyzeLeaks()
            # print('All mails processed.')
            end_time = time.time()
            print("Time elapsed: %s" % (end_time - start_time))
            print("Mails_left: %s" % mails_left)
            # print('%s have been processed until now.' % num_mails_processed)

        print("done")
        # Clean up zombie processes
        kill_openwpm()

        # if len(mailfetcher.models.mails_without_unsubscribe_link) != 0:
        #     print('Messages for which no unsubscribe links have been found:')
        #     for subject in mailfetcher.models.mails_without_unsubscribe_link:
        #         print(subject)
        # else:
        #     print('No messages without possible unsubscribe links found.')
        if server and thread:
            server.shutdown()
            server.socket.close()
            thread.join(5)
