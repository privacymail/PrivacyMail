from __future__ import absolute_import

import base64
import datetime
import email
import hashlib
import logging
import os
import re
import sqlite3 as lite
import statistics
import string
import sys
import urllib
from .Thirdparty import Thirdparty
from .Eresource import Eresource
from datetime import datetime as dt
from email.header import decode_header, make_header
from email.utils import parsedate_to_datetime
from random import choice, randint

import html2text
import tldextract
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import mail_admins
from django.db import connection, models
from django.db.models import Q
from django.db.utils import InterfaceError
from django.template.loader import render_to_string
from django.utils.functional import cached_property
from django_countries.fields import CountryField
from identity.models import Identity, Service, ServiceThirdPartyEmbeds
from identity.util import convertForJsonResponse
from Levenshtein import ratio
from model_utils import Choices
from OpenWPM.openwpm import CommandSequence, TaskManager
from six.moves import range


# from mailfetcher.models import Thirdparty, Eresource

mails_without_unsubscribe_link = []
logger = logging.getLogger(__name__)


class Mail(models.Model):
    PROCESSING_STATES = Choices(
        ("UNPROCESSED", "unprocessed"),
        ("VIEWED", "viewed"),
        ("LINK_CLICKED", "link_clicked"),
        ("DONE", "done"),
        ("NO_UNSUBSCRIBE_LINK", "no_unsubscribe_link"),
        ("FAILED", "failed"),
    )

    raw = models.TextField()
    message_id = models.TextField()
    body_plain = models.TextField(null=True, blank=True)
    body_html = models.TextField(null=True, blank=True)
    h_x_original_to = models.CharField(max_length=200, null=True, blank=True)
    h_from = models.CharField(max_length=200, null=True, blank=True)
    h_to = models.CharField(max_length=200, null=True, blank=True)
    h_cc = models.CharField(max_length=200, null=True, blank=True)
    h_bcc = models.CharField(max_length=200, null=True, blank=True)
    h_subject = models.CharField(max_length=500, null=True, blank=True)
    h_date = models.CharField(max_length=200, null=True, blank=True)
    date_time = models.DateTimeField(blank=True, null=True)
    h_user_agent = models.CharField(max_length=200, null=True, blank=True)
    identity = models.ManyToManyField(Identity, related_name="message")
    suspected_spam = models.BooleanField(default=False)
    mail_from_another_identity = models.ManyToManyField("self", symmetrical=True)
    possible_AB_testing = models.BooleanField(default=False)
    processing_state = models.CharField(
        choices=PROCESSING_STATES, default=PROCESSING_STATES.UNPROCESSED, max_length=20
    )
    processing_fails = models.IntegerField(default=0)
    contains_javascript = models.BooleanField(default=False)

    # The message will be saved here. It is not saved in the database and may be recalculated
    # Access by get_message

    message = None

    def __str__(self):
        return "({})|{} from {}".format(self.message_id, self.h_subject, self.h_from)

    # Creates the mail in the database and does some analysis. It still has to be run through OpenWPM!
    @classmethod
    def create(cls, raw_mail):
        message = raw_mail
        # print("raw={}".format(str(message)))

        message_raw = message.as_bytes().decode(encoding="UTF-8", errors="replace")
        message_id = message["Message-ID"]
        if message_id is None:
            message_id = "".join(
                choice(string.ascii_uppercase + string.digits) for _ in range(32)
            )
        print(
            "Message ID:",
            message_id,
            " Subject:",
            str(make_header(decode_header(cls._clear_none_values(message["subject"])))),
        )
        try:
            mail = Mail.objects.get(raw=message_raw)
            if mail.date_time is not None:
                return mail
        except ObjectDoesNotExist:
            mail = cls(raw=message_raw, message_id=message_id)
            mail.save()
        except InterfaceError:
            print(
                "###################################################################################"
            )
            print("Database Interface Error!\n")

            # reset the database connection
            from django.db import connection

            connection.connection.close()
            connection.connection = None
            sys.exit("Lost connection to database!")
            logger.error("Lost connection to the postgreSQL database!!")

        mail.message = message
        mail.calc_bodies()
        mail.calc_header()
        mail.extract_static_links()
        # mail.extract_diff()
        mail.check_for_approved_identity()
        mail.check_for_unusual_sender()
        mail.parse_h_date_create_datetime()
        # mail.get_non_unsubscribe_link()
        return mail

    def reset_for_recrawl(self, link_only=False):
        """Reset the state of this message to be ready for recrawling."""
        self.processing_fails = 0
        self.contains_javascript = False
        self.possible_AB_testing = False
        # Delete associated dynamic Eresources (leave static in)
        if link_only:
            # Delete only link click information, leave mail view unchanged
            Eresource.objects.filter(mail=self, type="con_click").delete()
            self.processing_state = self.PROCESSING_STATES.VIEWED
        else:
            # Also delete mail view
            Eresource.objects.filter(mail=self, type__contains="con").delete()
            self.processing_state = self.PROCESSING_STATES.UNPROCESSED
        self.save()

    # # Raw is an array of lines
    # @classmethod
    # def parse_raw(cls, raw):
    #     parser = email.parser.FeedParser()
    #     for line in raw[1]:
    #         parser.feed(str(line + b'\n', 'utf-8'))
    #     message = parser.close()
    #     return message

    def get_message(self):
        if self.message is None:
            parser = email.parser.FeedParser()
            parser.feed(self.raw)
            self.message = parser.close()
        return self.message

    def calc_bodies(self):
        message = self.get_message()
        # print("Mail to: " + message['To'])
        body_plain = None
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

        self.body_html = body_html
        self.body_plain = body_plain
        try:
            self.save()
        except ValueError:
            # Postgresql does not allow nullbytes.
            if self.body_html is None:
                self.body_html = ""
            if self.body_plain is None:
                self.body_plain = ""
            self.body_html = self.body_html.replace("\x00", "")
            self.body_plain = self.body_plain.replace("\x00", "")
            self.save()

    def calc_header(self):
        message = self.get_message()
        self.h_x_original_to = message["X-Original-To"]
        self.h_from = message["From"]
        self.h_to = message["To"]
        self.h_cc = message["Cc"]
        self.h_bcc = message["BCC"]
        self.h_subject = make_header(
            decode_header(self._clear_none_values(message["Subject"]))
        )
        self.h_date = message["Date"]
        self.h_user_agent = message["User-Agent"]
        # date_obj = parsedate_to_datetime(self.h_date)
        # self.date_time = date_obj

        identity_set = Identity.objects.filter(
            Q(mail__in=self.addresses_from_field(self.h_x_original_to))
            | Q(mail__in=self.addresses_from_field(self.h_to))
            | Q(mail__in=self.addresses_from_field(self.h_cc))
        )

        for ident in identity_set:
            self.identity.add(ident)
            ident.service.resultsdirty = True
            ident.service.save()
        self.save()

    def create_service_third_party_connections(self):
        # Connects a service to a third party if this connection has been observed
        identity = self.identity
        if identity.count() < 1:
            logger.error("Mail has no associated identity", extra={"mailID": self.pk})
            return
        service = identity.get().service
        for eresource in self.eresource_set.all():
            mail_leakage = eresource.mail_leakage is not None
            # Mail disclosure is also an identifier.
            receives_identifier = mail_leakage or eresource.personalised
            if eresource.response_headers is not None:
                sets_cookie = "Set-Cookie" in eresource.response_headers
            else:
                sets_cookie = False

            def embed_switcher(argument):
                switcher = {
                    "a": ServiceThirdPartyEmbeds.STATIC,
                    "img": ServiceThirdPartyEmbeds.STATIC,
                    "link": ServiceThirdPartyEmbeds.STATIC,
                    "script": ServiceThirdPartyEmbeds.STATIC,
                    "con": ServiceThirdPartyEmbeds.ONVIEW,
                    "con_click": ServiceThirdPartyEmbeds.ONCLICK,
                }
                return switcher.get(argument, ServiceThirdPartyEmbeds.UNDETERMINED)

            embed_type = embed_switcher(eresource.type)
            embedding, created = ServiceThirdPartyEmbeds.objects.get_or_create(
                service=service,
                thirdparty=eresource.host,
                leaks_address=mail_leakage,
                sets_cookie=sets_cookie,
                embed_type=embed_type,
                receives_identifier=receives_identifier,
                mail=self,
            )

    @staticmethod
    def addresses_from_field(field):
        def address_from_field(ad):
            ad = ad.strip()
            if "<" in ad:
                return re.search("<(.*)>", ad).group(1)
            return ad

        if field is not None:
            return [address_from_field(a) for a in field.split(",")]
        else:
            return []

    @staticmethod
    def _clear_none_values(value):
        if value is None:
            return ""
        return value

    # Try to get a link for openWPM to click, which isn't an unsubscribe link.
    # In most cases it should be enough to only click one link, because if tracking occurs, every link should track.
    def get_non_unsubscribe_link(self):
        type_a_urls = Eresource.objects.filter(
            type="a", mail_id=self.id, possible_unsub_link=False
        )
        if type_a_urls.count() < 1:
            print(
                "############################### Did not find possible unsubscribe link!"
            )
            return ""

        while type_a_urls.count() > 1:
            rand = randint(0, type_a_urls.count() - 1)
            chosen_url = type_a_urls[rand].url
            if "http" in chosen_url:
                return chosen_url
            type_a_urls.exclude(url=chosen_url)

        # print('Chosen URL to click: %s' % type_a_urls[rand])
        return ""

    def extract_static_links(self):
        # extract external resources for more detailed analysis
        if not self.body_html:
            # TODO Do we want to analyze links of plaintext mails?
            # The mail includes no html, but just plain text info
            return
        soup = BeautifulSoup(self.body_html, "html.parser")
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

        num_detected_unsub_links = 0
        for link in a_links:
            if Eresource.is_unsub_word_in_link(link):
                num_detected_unsub_links = num_detected_unsub_links + 1
                if settings.DEVELOP_ENVIRONMENT:
                    print("Found possible unsubscribe link: %s" % link)
        if num_detected_unsub_links < 1:
            message = self.get_message()
            mail_subject = make_header(
                decode_header(self._clear_none_values(message["Subject"]))
            )
            logger.debug(
                "No unsubscribe link was found.",
                extra={
                    "mail_subject": str(mail_subject),
                },
            )
            print("Did not find a possible unsubscribe link!")

        # First and last links in e-mail are more likely to be unsubscribe links.
        if len(a_links) > 2 * settings.NUM_LINKS_TO_SKIP:
            for i in range(settings.NUM_LINKS_TO_SKIP):
                first_link = a_links.pop(0)
                last_link = a_links.pop()

                Eresource.create_clickable(first_link, True, self)
                Eresource.create_clickable(last_link, True, self)

        for link in a_links:
            if "http" not in link["href"]:
                continue
            unsub_word_in_link = Eresource.is_unsub_word_in_link(link)
            Eresource.create_clickable(link, unsub_word_in_link, self)

        for img in soup.find_all("img"):
            Eresource.create_static_eresource(img, "src", self)

        for link in soup.find_all("link"):
            Eresource.create_static_eresource(link, "href", self)

        for script in soup.find_all("script"):
            Eresource.create_static_eresource(script, "src", self)

    # Deprecated, not used.
    def extract_diff(self):
        hashdictowner = None
        hashdictmatch = None
        # get all mails of the same service
        samemails = Mail.objects.filter(
            identity__service__in=Service.objects.filter(
                identity__in=self.identity.all()
            )
        )

        # filter the list to a list of mails with same subject, but exclude the originalto header
        samemails = samemails.filter(h_subject=self.h_subject).exclude(
            h_x_original_to=self.h_x_original_to
        )
        # iterate through all mails from different identities to check if eresources differ
        for email in samemails:
            # link same emails together
            self.mail_from_another_identity.add(email)

            # get eresources from these mails
            actual = Eresource.objects.filter(mail=email).values("url")
            # get eresource form this mail
            expected = Eresource.objects.filter(mail=self).values("url")

            if len(actual) != len(expected):
                # TODO increase performance and extract interesting data
                print(
                    "Different number of Eresources for same mail on different identities!"
                )
                continue

            # compare urls if they dont match set the differentsource field to the eresource object which is same
            # same but different (contains other id etc.)
            for idx, url in enumerate(expected):
                try:
                    if not str(url.values()) == str(actual[idx].values()):
                        # print(url.values())
                        # print(actual[idx].values())
                        matchobject = (
                            Eresource.objects.filter(mail=email)
                            .filter(url__in=actual[idx].values())[:1]
                            .get()
                        )
                        owneresource = (
                            Eresource.objects.filter(mail=self)
                            .filter(url__in=url.values())[:1]
                            .get()
                        )

                        # link eresource together
                        matchobject.diff_eresource = owneresource
                        matchobject.save()
                        owneresource.diff_erentsource = matchobject
                        owneresource.save()
                        # TODO: wird jetzt nur ausgeführt wenn mails mehrfach da sind und sich links unterscheiden.
                        # Was ist wenn die mail auf nur einer identität angekommen ist?

                        # make sure the dicts are only generated once
                        if not hashdictowner:
                            hashdictowner = self.generate_match_dict(
                                owneresource.mail.h_x_original_to
                            )
                        if not hashdictmatch:
                            hashdictmatch = self.generate_match_dict(
                                matchobject.mail.h_x_original_to
                            )

                        Mail.analyze_eresource(owneresource, hashdictowner)
                        Mail.analyze_eresource(matchobject, hashdictmatch)

                except IndexError:
                    print("Number of resources does not match!")

        self.save()

    def get_similar_mails_of_different_identities(self):
        mail_date = self.date_time
        earliest_date = mail_date - datetime.timedelta(
            minutes=11 * 60 + 30
        )  # 11 hours and 30 minutes
        last_date = mail_date + datetime.timedelta(minutes=11 * 60 + 30)
        mails_in_timeframe = Mail.objects.filter(
            date_time__range=(earliest_date, last_date)
        )

        service_mail_set = mails_in_timeframe.filter(
            identity__service__in=Service.objects.filter(
                identity__in=self.identity.all()
            )
        ).exclude(h_x_original_to=self.h_x_original_to)
        similar_mails = []
        for mail in service_mail_set:
            if ratio(self.h_subject, mail.h_subject) > 0.9:
                similar_mails.append(mail)
        return similar_mails

    def parse_h_date_create_datetime(self):
        try:
            dateObj = parsedate_to_datetime(self.h_date)
        except TypeError:
            # Email did not provide a date
            dateObj = datetime.datetime.now()
        self.date_time = dateObj
        self.save()

    def get_similar_links(self, mail, print_links=False):
        """
        :param mail:
        :param print_links: prints the links with X for the chars that are different.
        :return: list with links, num_different_links, total_num_links, min_difference, max_difference, mean, median
        """
        mail1_eresources = (
            Eresource.objects.filter(mail=self, personalised=False)
            .exclude(type="con")
            .exclude(type="con_click")
        )
        mail2_eresources = (
            Eresource.objects.filter(mail=mail, personalised=False)
            .exclude(type="con")
            .exclude(type="con_click")
        )
        num_different_links = 0
        min_difference = 5000
        max_difference = 0
        list_differences = []
        own_mail_link_set = self.extract_static_links_of_mail()
        similar_mail_link_set = mail.extract_static_links_of_mail()
        l1 = len(own_mail_link_set)
        l2 = len(similar_mail_link_set)
        links = []
        if l1 != l2:
            # print('Different number of links in the compared 2 mails.')
            # print('Id of first mail: {}. Subject:{}'.format(self.id, self.h_subject))
            # print('Id of second mail: {}. Subject:{}'.format(mail.id, mail.h_subject))
            logger.warning(
                "Different number of links in the compared 2 mails.",
                extra={"ID first mail": self.id, "ID second mail": mail.id},
            )
            return [], -1, -1, -1, -1, -1, -1
        for counter, link in enumerate(own_mail_link_set):
            link1 = link
            link2 = similar_mail_link_set[counter]
            length = len(link1)
            if len(link2) < len(link1):
                length = len(link2)

            index = [i for i in range(length) if link1[i] != link2[i]]

            if len(index) < 1:
                continue
            # Mark eresources as personalised.
            mail1_eresource = mail1_eresources.filter(url=link1)
            for eresource in mail1_eresource:
                eresource.personalised = True
                eresource.save()
            mail2_eresource = mail2_eresources.filter(url=link2)
            for eresource in mail2_eresource:
                eresource.personalised = True
                eresource.save()

            if len(index) < min_difference:
                min_difference = len(index)
            if len(index) > max_difference:
                max_difference = len(index)
            num_different_links += 1
            list_differences.append(len(index))
            for i in index:
                link = link[:i] + "X" + link[i + 1 :]
            # print('Next Mail')
            links.append(link)
        if print_links:
            for link in links:
                print(link)
        try:
            if len(list_differences) == 0:
                list_differences.append(0)
            if min_difference == 5000:
                min_difference = 0
            return (
                links,
                num_different_links,
                l1,
                min_difference,
                max_difference,
                statistics.mean(list_differences),
                statistics.median(list_differences),
            )
        except statistics.StatisticsError:
            return (
                links,
                num_different_links,
                l1,
                min_difference,
                max_difference,
                -1,
                -1,
            )
        # l = [i for i in range(len(s1)) if s1[i] != s2[i]]

    def compare_text_of_mails(self, mail):
        """ Compare the html body of two mails via string similarity """

        def get_new_html_handler():
            html_handler = html2text.HTML2Text()
            # Ignore converting links from HTML
            html_handler.ignore_links = True
            # Also get rid of images/links and leave the alt text.
            html_handler.images_to_alt = True
            return html_handler

        try:
            without_html1 = get_new_html_handler().handle(self.body_html)
            without_html2 = get_new_html_handler().handle(mail.body_html)
        except AttributeError:
            # Has no body_html.
            without_html1 = get_new_html_handler().handle("")
            without_html2 = get_new_html_handler().handle("")
        # Remove the name and domain from the resulting text.
        id1 = self.identity.all()
        id2 = mail.identity.all()

        def remove_name(identity, text):
            first_name = identity.first_name.lower()
            last_name = identity.surname.lower()
            address = identity.mail
            cleaned = re.sub(address, "", text, flags=re.IGNORECASE)
            cleaned = re.sub(last_name, "", cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(first_name, "", cleaned, flags=re.IGNORECASE)
            return cleaned

        if id1.count() > 0 and id2.count() > 0:
            cleaned1 = remove_name(id1[0], without_html1)
            cleaned1 = remove_name(id2[0], cleaned1)
            cleaned2 = remove_name(id1[0], without_html2)
            cleaned2 = remove_name(id2[0], cleaned2)
        else:
            return -1

        similarity = ratio(cleaned1, cleaned2)
        differences = ""
        if similarity < 0.9993:
            differences = Mail.inline_diff(cleaned1, cleaned2)

        return similarity, differences

    # From https://stackoverflow.com/questions/774316/python-difflib-highlighting-differences-inline/788780#788780
    @staticmethod
    def inline_diff(a, b):
        import difflib

        matcher = difflib.SequenceMatcher(None, a, b)

        def process_tag(tag, i1, i2, j1, j2):
            if tag == "replace":
                return "{" + matcher.a[i1:i2] + " -> " + matcher.b[j1:j2] + "}"
            if tag == "delete":
                return "{- " + matcher.a[i1:i2] + "}"
            if tag == "equal":
                # return matcher.a[i1:i2]
                return ""
            if tag == "insert":
                return "{+ " + matcher.b[j1:j2] + "}"
            assert False, "Unknown tag %r" % tag

        return "".join(process_tag(*t) for t in matcher.get_opcodes())

    def extract_static_links_of_mail(self):
        if not self.body_html:
            # TODO Do we want to analyze links of plaintext mails?
            # The mail includes no html, but just plain text info
            return []
        soup = BeautifulSoup(self.body_html, "html.parser")
        script_elements = [element["src"] for element in soup.select("script[src]")]
        anchor_elements = [element["href"] for element in soup.select("a[href]")]
        link_elements = [element["href"] for element in soup.select("link[href]")]
        image_elements = [element["src"] for element in soup.select("img[src]")]

        links = script_elements + anchor_elements + link_elements + image_elements
        cleaned_links = []
        for link in links:
            if "data:image" in link:
                continue
            elif "mailto" in link:
                continue
            li = "".join(link.split())
            cleaned_links.append(li)
        return cleaned_links

    @staticmethod
    def analyze_eresource(eresource, dict):
        # check for leakage and if yes, set matched algorithm combination
        # case insensitive
        for key, val in dict.items():
            if (
                str(val) in eresource.url
                or str(val).casefold() in eresource.url.replace("-", "").casefold()
            ):
                if eresource.mail_leakage is None or eresource.mail == "":
                    eresource.mail_leakage = key
                else:
                    if key in eresource.mail_leakage:
                        continue
                    eresource.mail_leakage = eresource.mail_leakage + ", " + key
                eresource.save()
                # print('Found leakage!')
                # break

    @staticmethod
    def generate_match_dict(mailaddr):
        hashdict = {}
        encdict = {}

        hashdict.update({"Mailaddress": mailaddr})
        hashdict.update({"Email Account": mailaddr.split("@")[0]})
        hashdict.update({"Address Domain": mailaddr.split("@")[1]})

        def create_upper_lower(dict, only_up=False):
            tempdict = {}
            for key, value in dict.items():
                if not key.startswith("up"):
                    tempdict.update({"up(" + key + ")": value.upper()})
                if only_up:
                    continue
                if (
                    not key.startswith("plain")
                    and not key.startswith("low")
                    and not key.startswith("domain")
                ):
                    tempdict.update({"low(" + key + ")": value.lower()})
            return tempdict

        def create_algo_dict(old_dict):
            algorithms = ["md5", "md4", "sha1", "sha256", "sha512", "sha384"]
            # Add upper and lower versions to be hashed, but don't add those to the enc dict. Comparison takes place on
            # casefold URL
            temp_dict = create_upper_lower(old_dict, True)
            temp_dict.update(old_dict)
            new_dict = {}
            for key, value in temp_dict.items():
                for algo in algorithms:
                    h = hashlib.new(algo)
                    h.update(value.encode("utf8"))
                    new_dict.update({algo + "(" + key + ")": h.hexdigest()})
            return new_dict

        hashdict.update(create_algo_dict(hashdict))

        # One level of nesting
        hashdict.update(create_algo_dict(hashdict))

        encdict = {}

        for key, val in hashdict.items():
            encdict.update(
                {
                    "base64("
                    + key
                    + ")": base64.b64encode(val.encode("utf8")).decode(
                        "utf-8", "replace"
                    )
                }
            )

        encdict.update({"urlencode(plain)": urllib.parse.quote(mailaddr)})

        # put dicts together
        hashdict.update(encdict)

        return hashdict

    def check_for_approved_identity(self):
        for ident in self.identity.all():
            now = dt.now()
            delta = datetime.timedelta(hours=settings.REMINDER_MAIL_THRESHOLD_IN_HOURS)
            # todo check this (approved identity)
            # print(not ident.approved and (ident.lastapprovalremindersend is None or ident.lastapprovalremindersend > (now + delta).time()))
            if not ident.approved and (
                ident.lastapprovalremindersend is None
                or ident.lastapprovalremindersend > (now + delta).time()
            ):
                message = render_to_string(
                    "identity_approval_mail.txt",
                    {"ident": ident, "mail": self, "URL": settings.SYSTEM_ROOT_URL},
                )
                subject = "A new identity needs approval"
                if not settings.DISABLE_ADMIN_MAILS:
                    mail_admins(subject, message)
                ident.lastapprovalremindersend = now
                ident.save()

    def check_for_unusual_sender(self):
        for ident in self.identity.all():
            for permitted_domain in ident.service.permitted_senders:
                if permitted_domain in self.h_from:
                    self.suspected_spam = False
                    self.save()
                    return
            # If we reach this point, h_from is not in any permitted sender list
            # Set it to be suspected spam and send a notification.
            self.suspected_spam = True
            subject = "Third-Party spam is suspected"
            message = render_to_string(
                "third_party_spam.txt",
                {"ident": ident, "mail": self, "URL": settings.SYSTEM_ROOT_URL},
            )
            if not settings.DISABLE_ADMIN_MAILS:
                mail_admins(subject, message)
            self.save()

    @staticmethod
    def connect_tracker(eresource):
        extracturl = tldextract.extract(eresource.url)
        host = "{}.{}".format(extracturl.domain, extracturl.suffix)

        # Don't save our own domain as third party.
        localDomain = tldextract.extract(settings.LOCALHOST_URL)
        localHost = "{}.{}".format(localDomain.domain, localDomain.suffix)
        if localHost in host:
            return

        try:
            thirdparty = Thirdparty.objects.get(name=host, host=host)
        except ObjectDoesNotExist:
            thirdparty = Thirdparty.create(name=host, host=host)
        eresource.host = thirdparty
        eresource.save()
        thirdparty.set_dirty()

    @cached_property
    def get_cleartext(self):
        if self.body_plain:
            return self.body_plain
        # Convert html to Markdown
        if self.body_html:
            return html2text.html2text(self.body_html)
        return ""

    @cached_property
    def hosts(self):
        return set([ident.service.url for ident in self.identity.all()])

    @cached_property
    def first_third_party_links(self):
        return self.first_third_party_by_type("a")

    @cached_property
    def first_third_party_connections(self):
        return self.first_third_party_by_type("con")

    def first_third_party_by_type(self, type):
        # Get all of this mail
        assets = Eresource.objects.filter(mail=self, type=type)
        first_party_personalized = 0
        first_party = 0
        third_party_personalized = 0
        third_party = 0
        for asset in assets:
            extract = tldextract.extract(asset.url)
            domain = "{}.{}".format(extract.domain, extract.suffix)
            if asset.personalized:
                if domain in self.hosts:
                    first_party_personalized += 1
                else:
                    third_party_personalized += 1
            else:
                if domain in self.hosts:
                    first_party += 1
                else:
                    third_party += 1
        return (
            first_party,
            first_party_personalized,
            third_party,
            third_party_personalized,
        )

    def get_service(self):
        identities = self.identity.all()
        try:
            return identities[0].service
        except:
            return None
