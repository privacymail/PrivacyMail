from django_cron import CronJobBase, Schedule
import poplib
from mailfetcher.models import Mail
from django.conf import settings
import imaplib
import email
import email.header
import logging
from django.core.cache import cache
import requests

poplib._MAXLINE = 20480
logger = logging.getLogger(__name__)


class ImapFetcher(CronJobBase):
    RUN_EVERY_MINS = 5

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'org.privacy-mail.imapfetcher-noanalyze'  # a unique code

    def notify_webhook(self, case):
        if settings.CRON_WEBHOOKS:
            try:
                url = settings.CRON_WEBHOOKS['mailfetcher.cron.ImapFetcher'][case]
                if url:
                    requests.get(url)
            except Exception:
                logger.warning("ImapFetcher.notify_webhook: Failed to send signal.", exc_info=True)
                # No matter what happens here
                pass

    def do(self):
        self.notify_webhook('start')
        cache.delete('ImapFetcher')

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
                        Mail.create(raw)
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
                except Exception:
                    logger.error("fetch_new_messages: Uncaught exception handled.", exc_info=True)
                    return -1

            print('All inboxes are empty. No new mails to process.')
            return 0

        self.notify_webhook('success')
