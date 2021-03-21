import psutil
import signal
import os
import email
import time
from mailfetcher.models import Mail, Eresource
from django.conf import settings
from mailfetcher.crons.mailCrawler.analysis.leakage import (
    analyze_mail_connections_for_leakage,
    analyze_single_mail_for_leakage,
)
from mailfetcher.crons.mailCrawler.analysis.viewMail import (
    call_openwpm_view_mail,
    call_openwpm_view_single_mail,
)
from mailfetcher.crons.mailCrawler.analysis.clickLinks import (
    call_openwpm_click_links,
)
from mailfetcher.crons.mailCrawler.singleMail import (
    get_stats_of_mail,
)
from mailfetcher.crons.mailCrawler.init import init
from bs4 import BeautifulSoup


def kill_openwpm(ignore=[]):
    for proc in psutil.process_iter():
        # check whether the process name matches
        if proc.pid in ignore:
            continue
        created = time.time() - proc.create_time()
        #kill only zombie processes that are older than two hours so not to disrupt other processes using openwpm
        if proc.name() in ["geckodriver", "firefox", "firefox-bin", "Xvfb"] and created >= 7200 :
            # Kill process tree
            gone, alive = kill_proc_tree(proc.pid)
            for p in alive:
                ignore.append(p.pid)
            # Recursively call yourself to avoid dealing with a stale PID list
            return kill_openwpm(ignore=ignore)


def kill_proc_tree(
    pid, sig=signal.SIGTERM, include_parent=True, timeout=1, on_terminate=None
):
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
    gone, alive = psutil.wait_procs(children, timeout=timeout, callback=on_terminate)
    return (gone, alive)


def analyzeOnView():
    # Load Mail Queue
    mail_queue = Mail.objects.filter(
        processing_state=Mail.PROCESSING_STATES.UNPROCESSED
    ).exclude(processing_fails__gte=settings.OPENWPM_RETRIES)[
        : settings.CRON_MAILQUEUE_SIZE
    ]
    mail_queue_count = mail_queue.count()

    if settings.RUN_OPENWPM and mail_queue_count > 0:
        print("Viewing %s mails." % mail_queue_count)
        # Analyze the email queue
        failed_mails = call_openwpm_view_mail(mail_queue)
        print(
            "{} mail views of {} failed in openWPM.".format(
                len(failed_mails), mail_queue_count
            )
        )

    # Clean up zombie processes
    kill_openwpm()

def analyzeSingleMail(mail):

    init()
    message = email.message_from_string(mail)
    body_html = calc_bodies(message)
    eresources = None
    # if settings.RUN_OPENWPM and mail:
    staticeresources = extract_static_eresources(body_html)
    eresources = call_openwpm_view_single_mail(body_html)
    eresources = staticeresources + eresources
    kill_openwpm()
    if "X-Original-To" in message:
        to = message["X-Original-To"]
    else:
        to = message["To"]
    service_url = message["From"].split("@")[1].replace(">", "")
    print(service_url)
    eresources = analyze_single_mail_for_leakage(to, eresources)
    stats = get_stats_of_mail(service_url, eresources)
    stats["cookies"] = analyze_cookies(eresources)
    return stats


def extract_static_eresources(body_html):
    static_eresources = []
    soup = BeautifulSoup(body_html, "html.parser")
    a_links = []
    for a in soup.find_all("a"):
        # prevent duplicate entries
        try:
            # skip mailtos
            if "mailto:" in a["href"]:
                continue
            # Touch the href
            a["href"]
        except KeyError:
            # print("a tag has no href attribute")
            # print(a.attrs)
            continue
        # Remove whitespace and newlines.
        # if a is not None:
        a["href"] = "".join(a["href"].split())
        a_links.append(a)

    for link in a_links:
        if "http" not in link["href"]:
            continue
        static_eresources.append(
            create_static_eresource(
                "a", link["href"], str(link.attrs) + str(link.contents)
            )
        )

    for img in soup.find_all("img"):
        static_eresources.append(
            create_static_eresource(
                img.name, img["src"], str(img.attrs) + str(img.contents)
            )
        )

    for link in soup.find_all("link"):
        static_eresources.append(
            create_static_eresource(
                link.name, link["href"], str(link.attrs) + str(link.contents)
            )
        )

    for script in soup.find_all("script"):
        static_eresources.append(
            create_static_eresource(
                script.name, script["src"], str(script.attrs) + str(script.contents)
            )
        )
    return static_eresources


def create_static_eresource(eresource_type, url, param):
    return {
        "type": eresource_type,
        "url": url,
        "possible_unsub_link": False,
        "param": param,
        "is_end_of_chain": True,
        "is_start_of_chain": True,
        "redirects_to_channel_id": None,
        "channel_id": None,
    }


def calc_bodies(message):
    # print("Mail to: " + message['To'])
    body_html = None
    if message.is_multipart():
        for part in message.walk():
            ctype = part.get_content_type()
            cdispo = str(part.get("Content-Disposition"))
            charset = part.get_param("CHARSET")
            # print("ctype={}; cdispo={}; charset={}".format(ctype, cdispo, charset))
            if charset is None:
                charset = "utf-8"
            # skip any text/plain (txt) attachments
            if ctype == "text/plain" and "attachment" not in cdispo:
                try:
                    body_plain = part.get_payload(decode=True).decode(charset)
                except UnicodeDecodeError:
                    body_plain = part.get_payload()

                # body_plain = part.get_payload(decode=True).decode(charset)  # decode
            if ctype == "text/html" and "attachment" not in cdispo:
                try:
                    body_html = part.get_payload(decode=True).decode(charset)
                except UnicodeDecodeError:
                    body_html = part.get_payload()
                # body_html = part.get_payload(decode=True).decode(charset)  # decode
    # not multipart - i.e. plain text, no attachments, keeping fingers crossed
    else:
        ctype = message.get_content_type()
        cdispo = str(message.get("Content-Disposition"))
        charset = message.get_param("CHARSET")
        # print("ctype={}; cdispo={}; charset={}".format(ctype, cdispo, charset))
        if charset is None:
            charset = "utf-8"
        if ctype == "text/plain" and "attachment" not in cdispo:

            try:
                body_plain = message.get_payload(decode=True).decode(charset)
            except UnicodeDecodeError:
                body_plain = message.get_payload()
            # body_plain = message.get_payload(decode=True).decode(charset)
        if ctype == "text/html" and "attachment" not in cdispo:

            try:
                body_html = message.get_payload(decode=True).decode(charset)
            except UnicodeDecodeError:
                body_html = message.get_payload()

            # body_html = message.get_payload(decode=True).decode(charset)
    # print(body_html)
    return body_html


def analyze_cookies(eresources):
    sets_cookie = False
    for eresource in eresources:
        if "response_headers" in eresource:
            sets_cookie = "Set-Cookie" in eresource["response_headers"]
            if sets_cookie:
                return sets_cookie
        else:
            sets_cookie = False
    return sets_cookie


def analyzeOnClick():
    # Load Mail Queue
    mail_queue = Mail.objects.filter(
        processing_state=Mail.PROCESSING_STATES.VIEWED
    ).exclude(processing_fails__gte=settings.OPENWPM_RETRIES)[
        : settings.CRON_MAILQUEUE_SIZE
    ]

    mail_queue_count = mail_queue.count()
    # Now we want to click some links
    if settings.VISIT_LINKS and settings.RUN_OPENWPM and mail_queue_count > 0:
        link_mail_map = {}
        print("Visiting %s links." % mail_queue_count)
        for mail in mail_queue:
            # Get a link that is not an unsubscribe link
            link = mail.get_non_unsubscribe_link()
            if "http" in link:
                link_mail_map[link] = mail
            else:
                print(
                    "Couldn't find a link to click for mail: {}. Skipping.".format(mail)
                )
                mail.processing_state = Mail.PROCESSING_STATES.NO_UNSUBSCRIBE_LINK
                mail.save()
        # Visit the links
        failed_urls = call_openwpm_click_links(link_mail_map)
        print(
            "{} urls of {} failed in openWPM.".format(
                len(failed_urls), mail_queue_count
            )
        )


def analyzeLeaks():
    # Load Mail Queue
    if settings.VISIT_LINKS:
        mail_queue = Mail.objects.filter(
            processing_state=Mail.PROCESSING_STATES.LINK_CLICKED
        )
    else:
        mail_queue = Mail.objects.filter(processing_state=Mail.PROCESSING_STATES.VIEWED)

    print("Analyzing {} mails for leakages.".format(mail_queue.count()))
    # Check if the email address is leaked somewhere (hashes, ...)
    for mail in mail_queue:
        analyze_mail_connections_for_leakage(mail)
        mail.create_service_third_party_connections()
        mail.processing_state = Mail.PROCESSING_STATES.DONE
        service = mail.get_service()
        if service is not None:
            service.resultsdirty = True
            service.save()
        mail.save()
