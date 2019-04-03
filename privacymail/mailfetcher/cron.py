from django_cron import CronJobBase, Schedule
import poplib
from mailfetcher.models import Mail
from django.conf import settings
import threading
import time
import imaplib
import email
import email.header
import http.server
import mailfetcher.models
import logging
from django.core.cache import cache
import psutil
import signal
import os

poplib._MAXLINE = 20480
logger = logging.getLogger(__name__)


class ImapFetcher(CronJobBase):
    RUN_EVERY_MINS = 5

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'org.privacy-mail.imapfetcher'  # a unique code

    def do(self):
        cache.delete('ImapFetcher')

        PORT = 5000
        DIRECTORY = "/tmp/"

        class Handler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=DIRECTORY, **kwargs)

        server = http.server.HTTPServer(('127.0.0.1', PORT), Handler)

        def startThread():
            # create a dummy favicon.ico
            open('/tmp/favicon.ico', 'a').close()
            thread = threading.Thread(target=server.serve_forever)
            thread.deamon = True
            thread.start()
            print("--- WEB Server started on port 5000 ---")
            return thread

        def kill_proc_tree(pid, sig=signal.SIGTERM, include_parent=True,
                           timeout=1, on_terminate=None):
            """Kill a process tree (including grandchildren) with signal
            "sig" and return a (gone, still_alive) tuple.
            "on_terminate", if specified, is a callabck function which is
            called as soon as a child terminates.
            """
            assert pid != os.getpid(), "won't kill myself"
            parent = psutil.Process(pid)
            children = parent.children(recursive=True)
            if include_parent:
                children.append(parent)
            for p in children:
                p.send_signal(sig)
            gone, alive = psutil.wait_procs(children, timeout=timeout,
                                            callback=on_terminate)
            return (gone, alive)

        def kill_openwpm(ignore=[]):
            for proc in psutil.process_iter():
                # check whether the process name matches
                if proc.pid in ignore:
                    continue
                if proc.name() in ["geckodriver", "firefox", "firefox-bin"]:
                    # Kill process tree
                    gone, alive = kill_proc_tree(proc.pid)
                    for p in alive:
                        ignore.append(p.pid)
                    # Recursively call yourself to avoid dealing with a stale PID list
                    return kill_openwpm(ignore=ignore)

        # Connect to the imapserver and select the INBOX mailbox.
        def imap_connect(mailserver):
            mailbox = imaplib.IMAP4_SSL(mailserver['MAILHOST'])
            response, data = mailbox.login(mailserver['MAILUSERNAME'], mailserver['MAILPASSWORD'])
            if response != 'OK':
                logger.error('imap_connect: Login to %s failed! Response: %s' % (mailserver['MAILHOST'], response))
                return None
            response, num_messages = mailbox.select('INBOX')
            if response != 'OK':
                logger.error('imap_connect: Unable to open INBOX on %s: %s' % (mailserver['MAILHOST'], response))
                return None

            response, list_of_messages = mailbox.search(None, "ALL")
            if response != 'OK':
                logger.error("imap_connect: Error while looking for messages in %s: %s" % (mailserver['MAILHOST'], response))
                mailbox.logout()
                return None
            return mailbox, list_of_messages

        # Fetch messages_to_fetch many mails from the mailserver and report how many were actually fetched.
        # Also adds them to the database as 'UNPROCESSED'
        def fetch_new_messages(num_mails_to_fetch):
            # Loop through all the mailservers in the settings to fetch new mails.
            for mailserver in settings.MAILCREDENTIALS:
                # # Don't loop when in developer mode
                # if settings.DEVELOP_ENVIRONMENT:
                #     mails_left = False
                try:
                    # print('Mailboxes: %s' % directories)
                    mailbox, list_of_messages = imap_connect(mailserver)
                    message_count = len(list_of_messages[0].split())
                    print('Server: ' + mailserver['MAILHOST'] + ', Number of messages: %s' % message_count)
                    messages_to_fetch = message_count
                    # Check whether there are more mails than we want in this round.
                    if messages_to_fetch > num_mails_to_fetch:
                        messages_to_fetch = num_mails_to_fetch
                    elif messages_to_fetch == 0:
                        continue
                    print('Queue size %s' % settings.CRON_MAILQUEUE_SIZE)

                    for i in range(1, messages_to_fetch + 1):
                        print("Parsing message: %s" % i)
                        response, data = mailbox.fetch(str(i), '(RFC822)')
                        if response != 'OK':
                            logger.warn("fetch_new_messages: ERROR fetching message %s from %s: %s" % (i, mailserver['MAILHOST'], response))
                            return

                        raw = email.message_from_bytes(data[0][1])
                        mail = Mail.create(raw)
                    mailbox.close()
                    mailbox.logout()

                    # Move processed mail to 'INBOX.processed' directory
                    if not settings.DEVELOP_ENVIRONMENT:
                        mailbox, list_of_messages = imap_connect(mailserver)
                        # Check whether the 'INBOX.processed' folder exists
                        response, data = mailbox.select('INBOX.processed')
                        if response == 'NO':
                            print('INBOX.processed mailbox does not exist. Creating it now...')
                            response, data = mailbox.create('INBOX.processed')
                            if response != 'OK':
                                logger.error('fetch_new_messages: Something went wrong while creating processed inbox folder on %s: %s, %s' % (mailserver['MAILHOST'], response, data))
                        # Switch back to the main INBOX
                        response, data = mailbox.select('INBOX')

                        # Move the messages to the processed directory
                        print('Moving mails to "processed" inbox.')
                        for i in range(1, messages_to_fetch + 1):
                            # print("Copying message %s to processed folder." % i)
                            response, data = mailbox.copy(str(i), 'INBOX.processed')
                            if response != 'OK':
                                logger.error("fetch_new_messages: error copying message %s on %s, Error: %s" % (i, mailserver['MAILHOST'], response))
                                return
                            response, data = mailbox.store(str(i), '+FLAGS', '\\Deleted')

                        print('Moved %s mails.' % messages_to_fetch)
                        mailbox.expunge()
                        mailbox.close()
                        mailbox.logout()
                    return messages_to_fetch
                except:
                    logger.error("fetch_new_messages: Uncaught exception handled.", exc_info=True)
                    return -1

            print('All inboxes are empty. No new mails to process.')
            return 0

        # Start measuring the time from the beginning.
        start_time = time.time()
        mails_left = True
        thread = startThread()

        # Continue until all mails processed.
        while mails_left:
            # Check whether there are too many mail in the database waiting to be processed.
            viewed_mails = Mail.objects.filter(processing_state=Mail.PROCESSING_STATES.VIEWED) \
                .exclude(processing_fails__gte=settings.OPENWPM_RETRIES).count()
            clicked_mails = Mail.objects.filter(processing_state=Mail.PROCESSING_STATES.LINK_CLICKED) \
                .exclude(processing_fails__gte=settings.OPENWPM_RETRIES).count()
            unprocessed_mails = Mail.objects.filter(processing_state=Mail.PROCESSING_STATES.UNPROCESSED) \
                .exclude(processing_fails__gte=settings.OPENWPM_RETRIES).count()
            failed_mails = Mail.objects.filter(processing_fails__gte=settings.OPENWPM_RETRIES).count()

            unfinished_mail_count = viewed_mails + clicked_mails + unprocessed_mails

            print('{} unprocessed mails in database. Additional {} mails are in failed state'
                  .format(unfinished_mail_count, failed_mails))
            print('{} unprocessed, {} viewed and {} link_clicked.'.format(unprocessed_mails, viewed_mails,
                                                                          clicked_mails))

            if unfinished_mail_count >= settings.CRON_MAILQUEUE_SIZE:
                print('Too many unfinished mails in database. Continuing without fetching new ones.')
            else:
                num_mails_to_fetch = settings.CRON_MAILQUEUE_SIZE - unfinished_mail_count
                # Get new messages from the mailserver
                messages_fetched = fetch_new_messages(num_mails_to_fetch)
                if messages_fetched == 0:
                    mails_left = False
                if messages_fetched == -1:
                    logger.warning('cron: An error occurred while fetching mails. Waiting and trying again.')
                    time.sleep(20)
                    continue

            # mailQueue.append(mail)
            mail_queue = Mail.objects.filter(processing_state=Mail.PROCESSING_STATES.UNPROCESSED
                                             ).exclude(processing_fails__gte=settings.OPENWPM_RETRIES
                                                       )[:settings.CRON_MAILQUEUE_SIZE]
            mail_queue_count = mail_queue.count()

            # if len(mail_queue) == 0:
            #     print('No mails in database which are "unprocessed".')
            #     continue

            # Run OpenWPM; View the Mail, then visit one of it's links.
            if settings.RUN_OPENWPM and mail_queue_count > 0:
                print('Viewing %s mails.' % mail_queue_count)
                failed_mails = Mail.call_openwpm_view_mail(mail_queue)
                print('{} mail views of {} failed in openWPM.'.format(len(failed_mails), mail_queue_count))

            mail_queue = Mail.objects.filter(processing_state=Mail.PROCESSING_STATES.VIEWED
                                             ).exclude(processing_fails__gte=settings.OPENWPM_RETRIES
                                                       )[:settings.CRON_MAILQUEUE_SIZE]
            mail_queue_count = mail_queue.count()

            # Clean up zombie processes
            kill_openwpm()

            if settings.VISIT_LINKS and settings.RUN_OPENWPM and mail_queue_count > 0:
                link_mail_map = {}
                print('Visiting %s links.' % mail_queue_count)
                for mail in mail_queue:
                    link = mail.get_non_unsubscribe_link()
                    if 'http' in link:
                        link_mail_map[link] = mail
                    else:
                        print("Couldn't find a link to click for mail: {}. Skipping.".format(mail))
                        mail.processing_state = Mail.PROCESSING_STATES.NO_UNSUBSCRIBE_LINK
                        mail.save()
                # Visit the links
                failed_urls = Mail.call_openwpm_click_links(link_mail_map)
                print('{} urls of {} failed in openWPM.'.format(len(failed_urls), mail_queue_count))

            if settings.VISIT_LINKS:
                mail_queue = Mail.objects.filter(processing_state=Mail.PROCESSING_STATES.LINK_CLICKED)
            else:
                mail_queue = Mail.objects.filter(processing_state=Mail.PROCESSING_STATES.VIEWED)

            print('Analyzing {} mails for leakages.'.format(mail_queue.count()))
            for mail in mail_queue:
                mail.analyze_mail_connections_for_leakage()
                mail.create_service_third_party_connections()
                mail.processing_state = Mail.PROCESSING_STATES.DONE
                service = mail.get_service()
                if service is not None:
                    service.resultsdirty = True
                    service.save()
                mail.save()

            # print('All mails processed.')
            end_time = time.time()
            print('Time elapsed: %s' % (end_time - start_time))
            print('Mails_left: %s' % mails_left)
            # print('%s have been processed until now.' % num_mails_processed)

        # Clean up zombie processes
        kill_openwpm()

        if len(mailfetcher.models.mails_without_unsubscribe_link) != 0:
            print('Messages for which no unsubscribe links have been found:')
            for subject in mailfetcher.models.mails_without_unsubscribe_link:
                print(subject)
        else:
            print('No messages without possible unsubscribe links found.')
        server.shutdown()
        server.socket.close()
        thread.join(5)
