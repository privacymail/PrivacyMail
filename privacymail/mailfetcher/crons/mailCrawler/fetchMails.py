from django.conf import settings

from mailfetcher.models import Mail
import imaplib
import email
import logging
import time

logger = logging.getLogger(__name__)

# fetches mails from the mailserver
# returns boolean if there are mails left on the server
def fetchMails(unfinished_mail_count):
    num_mails_to_fetch = settings.CRON_MAILQUEUE_SIZE - unfinished_mail_count
    # Get new messages from the mailserver
    messages_fetched = fetch_new_messages(num_mails_to_fetch)
    if messages_fetched == 0:
        return False
    if messages_fetched == -1:
        logger.warning(
            "cron: An error occurred while fetching mails. Waiting and trying again."
        )
        time.sleep(20)
        return True

    return True


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
            print(
                "Server: "
                + mailserver["MAILHOST"]
                + ", Number of messages: %s" % message_count
            )
            messages_to_fetch = message_count
            # Check whether there are more mails than we want in this round.
            if messages_to_fetch > num_mails_to_fetch:
                messages_to_fetch = num_mails_to_fetch
            elif messages_to_fetch == 0:
                continue
            print("Queue size %s" % settings.CRON_MAILQUEUE_SIZE)

            # Parse messages and place in database
            for i in range(1, messages_to_fetch + 1):
                print("Parsing message: %s" % i)
                response, data = mailbox.fetch(str(i), "(RFC822)")
                if response != "OK":
                    logger.warn(
                        "fetch_new_messages: ERROR fetching message %s from %s: %s"
                        % (i, mailserver["MAILHOST"], response)
                    )
                    return

                raw = email.message_from_bytes(data[0][1])
                mail = Mail.create(raw)
            mailbox.close()
            mailbox.logout()

            # Move processed mail to 'INBOX.processed' directory
            if not settings.DEVELOP_ENVIRONMENT:
                mailbox, list_of_messages = imap_connect(mailserver)
                # Check whether the 'INBOX.processed' folder exists
                response, data = mailbox.select("INBOX.processed")
                if response == "NO":
                    print("INBOX.processed mailbox does not exist. Creating it now...")
                    response, data = mailbox.create("INBOX.processed")
                    if response != "OK":
                        logger.error(
                            "fetch_new_messages: Something went wrong while creating processed inbox folder on %s: %s, %s"
                            % (mailserver["MAILHOST"], response, data)
                        )
                # Switch back to the main INBOX
                response, data = mailbox.select("INBOX")

                # Move the messages to the processed directory
                print('Moving mails to "processed" inbox.')
                for i in range(1, messages_to_fetch + 1):
                    # print("Copying message %s to processed folder." % i)
                    response, data = mailbox.copy(str(i), "INBOX.processed")
                    if response != "OK":
                        logger.error(
                            "fetch_new_messages: error copying message %s on %s, Error: %s"
                            % (i, mailserver["MAILHOST"], response)
                        )
                        return
                    response, data = mailbox.store(str(i), "+FLAGS", "\\Deleted")

                print("Moved %s mails." % messages_to_fetch)
                mailbox.expunge()
                mailbox.close()
                mailbox.logout()
            return messages_to_fetch
        except:
            logger.error(
                "fetch_new_messages: Uncaught exception handled.", exc_info=True
            )
            return -1

    print("All inboxes are empty. No new mails to process.")
    return 0


# Connect to the imapserver and select the INBOX mailbox.
def imap_connect(mailserver):
    mailbox = imaplib.IMAP4_SSL(mailserver["MAILHOST"])
    response, data = mailbox.login(
        mailserver["MAILUSERNAME"], mailserver["MAILPASSWORD"]
    )
    if response != "OK":
        logger.error(
            "imap_connect: Login to %s failed! Response: %s"
            % (mailserver["MAILHOST"], response)
        )
        return None
    response, num_messages = mailbox.select("INBOX")
    if response != "OK":
        logger.error(
            "imap_connect: Unable to open INBOX on %s: %s"
            % (mailserver["MAILHOST"], response)
        )
        return None

    response, list_of_messages = mailbox.search(None, "ALL")
    if response != "OK":
        logger.error(
            "imap_connect: Error while looking for messages in %s: %s"
            % (mailserver["MAILHOST"], response)
        )
        mailbox.logout()
        return None
    return mailbox, list_of_messages
