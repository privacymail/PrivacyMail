from __future__ import absolute_import
from six.moves import range
from OpenWPM.automation import CommandSequence, TaskManager
import sys
from random import randint
import email
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from bs4 import BeautifulSoup
import sqlite3 as lite
import hashlib
import os
import tldextract
from django.conf import settings
import tempfile
from identity.models import Identity, Service, ServiceThirdPartyEmbeds
import re
from datetime import datetime as dt
import datetime
from django.db import models
import html2text
from django.db.utils import InterfaceError
from django.utils.functional import cached_property
from django.core.mail import mail_admins
from django.template.loader import render_to_string
import base64
import urllib
from email.header import decode_header, make_header
from model_utils import Choices
from Levenshtein import ratio
from email.utils import parsedate_to_datetime
import statistics
import logging
from django.db import connection

mails_without_unsubscribe_link = []
logger = logging.getLogger(__name__)


class Mail(models.Model):
    PROCESSING_STATES = Choices(
        ('UNPROCESSED', 'unprocessed'),
        ('VIEWED', 'viewed'),
        ('LINK_CLICKED', 'link_clicked'),
        ('DONE', 'done'),
        ('NO_UNSUBSCRIBE_LINK', 'no_unsubscribe_link'),
        ('FAILED', 'failed')
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
    identity = models.ManyToManyField(Identity, related_name='message')
    suspected_spam = models.BooleanField(default=False)
    mail_from_another_identity = models.ManyToManyField("self", symmetrical=True)
    possible_AB_testing = models.BooleanField(default=False)
    processing_state = models.CharField(choices=PROCESSING_STATES, default=PROCESSING_STATES.UNPROCESSED, max_length=20)
    processing_fails = models.IntegerField(default=0)

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

        message_raw = message.as_bytes().decode(encoding='UTF-8', errors='replace')
        message_id = message['Message-ID']
        print("Message ID: " + message_id + " Subject: " + str(make_header(decode_header(message['subject']))))
        try:
            mail = Mail.objects.get(raw=message_raw)
            if mail.date_time is not None:
                return mail
        except ObjectDoesNotExist:
            mail = cls(raw=message_raw, message_id=message_id)
            mail.save()
        except InterfaceError:
            print('###################################################################################')
            print('Database Interface Error!\n')

            # reset the database connection
            from django.db import connection
            connection.connection.close()
            connection.connection = None
            sys.exit('Lost connection to database!')
            logger.error('Lost connection to the postgreSQL database!!')

        mail.message = message
        mail.calc_bodies()
        mail.calc_header()
        mail.extract_clickable_links()
        # mail.extract_diff()
        mail.check_for_approved_identity()
        mail.check_for_unusual_sender()
        mail.parse_h_date_create_datetime()
        # mail.get_non_unsubscribe_link()

        return mail

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
        print("Mail to: " + message['To'])
        body_plain = None
        body_html = None
        if message.is_multipart():
            for part in message.walk():
                ctype = part.get_content_type()
                cdispo = str(part.get('Content-Disposition'))
                charset = part.get_param('CHARSET')
                # print("ctype={}; cdispo={}; charset={}".format(ctype, cdispo, charset))
                if charset is None:
                    charset = 'utf-8'
                # skip any text/plain (txt) attachments
                if ctype == 'text/plain' and 'attachment' not in cdispo:
                    try:
                        body_plain = part.get_payload(decode=True).decode(charset)
                    except UnicodeDecodeError:
                        body_plain = part.get_payload()

                    # body_plain = part.get_payload(decode=True).decode(charset)  # decode
                if ctype == 'text/html' and 'attachment' not in cdispo:
                    try:
                        body_html = part.get_payload(decode=True).decode(charset)
                    except UnicodeDecodeError:
                        body_html = part.get_payload()
                    # body_html = part.get_payload(decode=True).decode(charset)  # decode
        # not multipart - i.e. plain text, no attachments, keeping fingers crossed
        else:
            ctype = message.get_content_type()
            cdispo = str(message.get('Content-Disposition'))
            charset = message.get_param('CHARSET')
            # print("ctype={}; cdispo={}; charset={}".format(ctype, cdispo, charset))
            if charset is None:
                charset = 'utf-8'
            if ctype == 'text/plain' and 'attachment' not in cdispo:

                try:
                    body_plain = message.get_payload(decode=True).decode(charset)
                except UnicodeDecodeError:
                    body_plain = message.get_payload()
                # body_plain = message.get_payload(decode=True).decode(charset)
            if ctype == 'text/html' and 'attachment' not in cdispo:

                try:
                    body_html = message.get_payload(decode=True).decode(charset)
                except UnicodeDecodeError:
                    body_html = message.get_payload()

                # body_html = message.get_payload(decode=True).decode(charset)

        self.body_html = body_html
        self.body_plain = body_plain
        self.save()

    def calc_header(self):
        message = self.get_message()
        self.h_x_original_to = message['X-Original-To']
        self.h_from = message['From']
        self.h_to = message['To']
        self.h_cc = message['Cc']
        self.h_bcc = message['BCC']
        self.h_subject = make_header(decode_header(message['Subject']))
        self.h_date = message['Date']
        self.h_user_agent = message['User-Agent']
        # date_obj = parsedate_to_datetime(self.h_date)
        # self.date_time = date_obj

        identity_set = Identity.objects.filter(Q(mail__in=self.addresses_from_field(self.h_x_original_to)) | Q(mail__in=self.addresses_from_field(self.h_to)) | Q(mail__in=self.addresses_from_field(self.h_cc)))

        for ident in identity_set:
            self.identity.add(ident)
            ident.service.resultsdirty = True
            ident.service.save()
        self.save()

    def create_service_third_party_connections(self):
        identity = self.identity
        if identity.count() < 1:
            logger.error('Mail has no associated identity', extra={'mailID': self.pk})
            return
        service = identity.get().service
        for eresource in self.eresource_set.all():
            mail_leakage = eresource.mail_leakage is not None
            if eresource.response_headers is not None:
                sets_cookie = 'Set-Cookie' in eresource.response_headers
            else:
                sets_cookie = False

            def embed_switcher(argument):
                switcher = {
                    'a': ServiceThirdPartyEmbeds.STATIC,
                    'con': ServiceThirdPartyEmbeds.ONVIEW,
                    'con_click': ServiceThirdPartyEmbeds.ONCLICK,
                }
                return switcher.get(argument, ServiceThirdPartyEmbeds.UNDETERMINED)

            embed_type = embed_switcher(eresource.type)
            embedding, created = ServiceThirdPartyEmbeds.objects.get_or_create(service=service,
                                                                               thirdparty=eresource.host,
                                                                               leaks_address=mail_leakage,
                                                                               sets_cookie=sets_cookie,
                                                                               embed_type=embed_type, mail=self)

    @staticmethod
    def addresses_from_field(field):
        def address_from_field(ad):
            ad = ad.strip()
            if '<' in ad:
                return re.search('<(.*)>', ad).group(1)
            return ad
        if field is not None:
            return [address_from_field(a) for a in field.split(',')]
        else:
            return []

    # Try to get a link for openWPM to click, which isn't an unsubscribe link.
    # In most cases it should be enough to only click one link, because if tracking occurs, every link should track.
    def get_non_unsubscribe_link(self):
        type_a_urls = Eresource.objects.filter(type='a', mail_id=self.id, possible_unsub_link=False)
        if type_a_urls.count() < 1:
            print('############################### Did not find possible unsubscribe link!')
            message = self.get_message()
            mails_without_unsubscribe_link.append(make_header(decode_header(message['Subject'])))
            return ''

        while type_a_urls.count() > 1:
            rand = randint(0, type_a_urls.count() - 1)
            chosen_url = type_a_urls[rand].url
            if 'http' in chosen_url:
                return chosen_url
            type_a_urls.exclude(url=chosen_url)

        # print('Chosen URL to click: %s' % type_a_urls[rand])
        return ''

    def extract_clickable_links(self):
        # extract external resources for more detailed analysis
        if not self.body_html:
            # TODO Do we want to analyze links of plaintext mails?
            # The mail includes no html, but just plain text info
            return
        soup = BeautifulSoup(self.body_html, 'html.parser')
        a_links = []
        for a in soup.find_all('a'):
            # prevent duplicate entries
            try:
                # skip mailtos
                if "mailto:" in a["href"]:
                    continue
                # Touch the href
                a["href"]
            except KeyError:
                print("a tag has no href attribute")
                print(a.attrs)
                continue
            # Remove whitespace and newlines.
            # if a is not None:
            a['href'] = ''.join(a['href'].split())
            a_links.append(a)

        num_detected_unsub_links = 0
        for link in a_links:
            if Eresource.is_unsub_word_in_link(link):
                num_detected_unsub_links = num_detected_unsub_links + 1
                if settings.DEVELOP_ENVIRONMENT:
                    print('Found possible unsubscribe link: %s' % link)
        if num_detected_unsub_links < 1:
            message = self.get_message()
            mail_subject = make_header(decode_header(message['Subject']))
            mails_without_unsubscribe_link.append(mail_subject)
            logger.debug('No unsubscribe link was found.', extra={
                'mail_subject': str(mail_subject),
            })
            print('Did not find a possible unsubscribe link!')

        # First and last links in e-mail are more likely to be unsubscribe links.
        if len(a_links) > 2 * settings.NUM_LINKS_TO_SKIP:
            for i in range(settings.NUM_LINKS_TO_SKIP):
                first_link = a_links.pop(0)
                last_link = a_links.pop()

                Eresource.create_clickable(first_link, True, self)
                Eresource.create_clickable(last_link, True, self)

        for link in a_links:
            if 'http' not in link['href']:
                continue
            unsub_word_in_link = Eresource.is_unsub_word_in_link(link)
            Eresource.create_clickable(link, unsub_word_in_link, self)

        for img in soup.find_all('img'):
            Eresource.create_static_eresource(img, 'src', self)

        for link in soup.find_all('link'):
            Eresource.create_static_eresource(link, 'href', self)

        for script in soup.find_all('script'):
            Eresource.create_static_eresource(script, 'src', self)

    def analyze_mail_connections_for_leakage(self):
        hashdict = None

        all_eresources = Eresource.objects.filter(mail=self).exclude(possible_unsub_link=True)
        if self.h_x_original_to is None:
            print ('Did not find mailaddress. Mail: {}'.format(self))
            return
        hashdict = Mail.generate_match_dict(self.h_x_original_to)
        for eresource in all_eresources:
            Mail.analyze_eresource(eresource, hashdict)

    def extract_diff(self):
        hashdictowner = None
        hashdictmatch = None
        # get all mails of the same service
        samemails = Mail.objects.filter(identity__service__in=Service.objects.filter(identity__in=self.identity.all()))

        # filter the list to a list of mails with same subject, but exclude the originalto header
        samemails = samemails.filter(h_subject=self.h_subject)\
                             .exclude(h_x_original_to=self.h_x_original_to)
        # iterate through all mails from different identities to check if eresources differ
        for email in samemails:
            # link same emails together
            self.mail_from_another_identity.add(email)

            # get eresources from these mails
            actual = Eresource.objects.filter(mail=email).values('url')
            # get eresource form this mail
            expected = Eresource.objects.filter(mail=self).values('url')

            if len(actual) != len(expected):
                # TODO increase performance and extract interesting data
                print('Different number of Eresources for same mail on different identities!')
                continue

            # compare urls if they dont match set the differentsource field to the eresource object which is same
            # same but different (contains other id etc.)
            for idx, url in enumerate(expected):
                try:
                    if not str(url.values()) == str(actual[idx].values()):
                        # print(url.values())
                        # print(actual[idx].values())
                        matchobject = Eresource.objects.filter(mail=email).filter(url__in=actual[idx].values())[:1].get()
                        owneresource = Eresource.objects.filter(mail=self).filter(url__in=url.values())[:1].get()

                        # link eresource together
                        matchobject.diff_eresource = owneresource
                        matchobject.save()
                        owneresource.diff_erentsource = matchobject
                        owneresource.save()
                        # TODO: wird jetzt nur ausgeführt wenn mails mehrfach da sind und sich links unterscheiden.
                        # Was ist wenn die mail auf nur einer identität angekommen ist?

                        # make sure the dicts are only generated once
                        if not hashdictowner:
                            hashdictowner = self.generate_match_dict(owneresource.mail.h_x_original_to)
                        if not hashdictmatch:
                            hashdictmatch = self.generate_match_dict(matchobject.mail.h_x_original_to)

                        Mail.analyze_eresource(owneresource, hashdictowner)
                        Mail.analyze_eresource(matchobject, hashdictmatch)

                except IndexError:
                    print("Number of resources does not match!")

        self.save()

    def get_similar_mails_of_different_identities(self):
        mail_date = self.date_time
        earliest_date = mail_date - datetime.timedelta(minutes=20)
        last_date = mail_date + datetime.timedelta(minutes=20)
        mails_in_timeframe = Mail.objects.filter(date_time__range=(earliest_date, last_date))

        service_mail_set = mails_in_timeframe.filter(identity__service__in=Service.objects.filter(identity__in=self.identity.all()))\
            .exclude(h_x_original_to=self.h_x_original_to)
        similar_mails = []
        for mail in service_mail_set:
            if ratio(self.h_subject, mail.h_subject) > 0.9:
                similar_mails.append(mail)
        return similar_mails

    def parse_h_date_create_datetime(self):
        dateObj = parsedate_to_datetime(self.h_date)
        self.date_time = dateObj
        self.save()

    def get_similar_links(self, mail, print_links=False):
        """
        :param mail:
        :param print_links: prints the links with X for the chars that are different.
        :return: list with links, num_different_links, total_num_links, min_difference, max_difference, mean, median
        """
        mail1_eresources = Eresource.objects.filter(mail=self, personalised=False).exclude(type='con').exclude(type='con_click')
        mail2_eresources = Eresource.objects.filter(mail=mail, personalised=False).exclude(type='con').exclude(type='con_click')
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
            logger.warning('Different number of links in the compared 2 mails.', extra={
                'ID first mail': self.id, 'ID second mail': mail.id})
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
                link = link[:i] + 'X' + link[i + 1:]
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
            return links, num_different_links, l1, min_difference, max_difference, statistics.mean(list_differences), \
               statistics.median(list_differences)
        except statistics.StatisticsError:
            return links, num_different_links, l1, min_difference, max_difference, -1, -1
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
            without_html1 = get_new_html_handler().handle('')
            without_html2 = get_new_html_handler().handle('')
        # Remove the name and domain from the resulting text.
        id1 = self.identity.all()
        id2 = mail.identity.all()

        def remove_name(identity, text):
            first_name = identity.first_name.lower()
            last_name = identity.surname.lower()
            address = identity.mail
            cleaned = re.sub(address, '', text, flags=re.IGNORECASE)
            cleaned = re.sub(last_name, '', cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(first_name, '', cleaned, flags=re.IGNORECASE)
            return cleaned

        if id1.count() > 0 and id2.count() > 0:
            cleaned1 = remove_name(id1[0], without_html1)
            cleaned1 = remove_name(id2[0], cleaned1)
            cleaned2 = remove_name(id1[0], without_html2)
            cleaned2 = remove_name(id2[0], cleaned2)
        else:
            return -1

        similarity = ratio(cleaned1, cleaned2)
        differences = ''
        if similarity < 0.9993:
            differences = Mail.inline_diff(cleaned1, cleaned2)

        return similarity, differences

    # From https://stackoverflow.com/questions/774316/python-difflib-highlighting-differences-inline/788780#788780
    @staticmethod
    def inline_diff(a, b):
        import difflib
        matcher = difflib.SequenceMatcher(None, a, b)

        def process_tag(tag, i1, i2, j1, j2):
            if tag == 'replace':
                return '{' + matcher.a[i1:i2] + ' -> ' + matcher.b[j1:j2] + '}'
            if tag == 'delete':
                return '{- ' + matcher.a[i1:i2] + '}'
            if tag == 'equal':
                # return matcher.a[i1:i2]
                return ''
            if tag == 'insert':
                return '{+ ' + matcher.b[j1:j2] + '}'
            assert False, "Unknown tag %r" % tag

        return ''.join(process_tag(*t) for t in matcher.get_opcodes())

    def extract_static_links_of_mail(self):
        if not self.body_html:
            # TODO Do we want to analyze links of plaintext mails?
            # The mail includes no html, but just plain text info
            return []
        soup = BeautifulSoup(self.body_html, 'html.parser')
        script_elements = [element['src'] for element in soup.select('script[src]')]
        anchor_elements = [element['href'] for element in soup.select('a[href]')]
        link_elements = [element['href'] for element in soup.select('link[href]')]
        image_elements = [element['src'] for element in soup.select('img[src]')]

        links = script_elements + anchor_elements + link_elements + image_elements
        cleaned_links = []
        for link in links:
            if 'data:image' in link:
                continue
            elif 'mailto' in link:
                continue
            li = ''.join(link.split())
            cleaned_links.append(li)
        return cleaned_links

    @staticmethod
    def analyze_eresource(eresource, dict):
        # check for leakage and if yes, set matched algorithm combination
        # case insensitive
        for key, val in dict.items():
            if str(val) in eresource.url or str(val).casefold() in eresource.url.replace('-', '').casefold():
                if eresource.mail_leakage is None or eresource.mail == '':
                    eresource.mail_leakage = key
                else:
                    if key in eresource.mail_leakage:
                        continue
                    eresource.mail_leakage = eresource.mail_leakage + ', ' + key
                eresource.save()
                # print('Found leakage!')
                # break

    @staticmethod
    def generate_match_dict(mailaddr):
        hashdict = {}
        encdict = {}

        hashdict.update({"Mailaddress": mailaddr})
        hashdict.update({"Email Account": mailaddr.split('@')[0]})
        hashdict.update({"Address Domain": mailaddr.split('@')[1]})

        def create_upper_lower(dict, only_up=False):
            tempdict = {}
            for key, value in dict.items():
                if not key.startswith('up'):
                    tempdict.update({'up(' + key + ')': value.upper()})
                if only_up:
                    continue
                if not key.startswith('plain') and not key.startswith('low') and not key.startswith('domain'):
                    tempdict.update({'low(' + key + ')': value.lower()})
            return tempdict

        def create_algo_dict(old_dict):
            algorithms = ['md5', 'md4', 'sha1', 'sha256', 'sha512', 'sha384']
            # Add upper and lower versions to be hashed, but don't add those to the enc dict. Comparison takes place on
            # casefold URL
            temp_dict = create_upper_lower(old_dict, True)
            temp_dict.update(old_dict)
            new_dict = {}
            for key, value in temp_dict.items():
                for algo in algorithms:
                    h = hashlib.new(algo)
                    h.update(value.encode("utf8"))
                    new_dict.update({algo + '(' + key + ')': h.hexdigest()})
            return new_dict

        hashdict.update(create_algo_dict(hashdict))

        # One level of nesting
        hashdict.update(create_algo_dict(hashdict))

        encdict = {}

        for key, val in hashdict.items():
            encdict.update({'base64(' + key + ')': base64.b64encode(val.encode("utf8")).decode("utf-8", "replace")})

        encdict.update({'urlencode(plain)': urllib.parse.quote(mailaddr)})

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
                    ident.lastapprovalremindersend is None or ident.lastapprovalremindersend > (now + delta).time()):
                message = render_to_string('identity_approval_mail.txt', {
                    'ident': ident,
                    'mail': self,
                    'URL': settings.SYSTEM_ROOT_URL
                })
                subject = "A new identity needs approval"
                if not settings.DISABLE_ADMIN_MAILS:
                    mail_admins(subject, message)
                ident.lastapprovalremindersend = now
                ident.save()

    def check_for_unusual_sender(self):
        for ident in self.identity.all():
            if ident.service.url not in self.h_from:
                self.suspected_spam = True
                subject = "Third-Party spam is suspected"
                message = render_to_string('third_party_spam.txt', {
                    'ident': ident,
                    'mail': self,
                    'URL': settings.SYSTEM_ROOT_URL
                })
                if not settings.DISABLE_ADMIN_MAILS:
                    mail_admins(subject, message)
                self.save()

    @staticmethod
    def call_openwpm_view_mail(mailQueue):
        print('Preparing data for OpenWPM.')
        wpm_db = settings.OPENWPM_DATA_DIR + "crawl-data.sqlite"
        if os.path.exists(wpm_db):
            os.remove(wpm_db)

        file_to_mail_map = {}
        mailFiles = []
        for mail in mailQueue:
            if mail.body_html:
                # create unique filename
                file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html')
                file.write(mail.body_html)
                file_basename = os.path.basename(file.name)
                filename = 'http://' + settings.LOCALHOST_URL + '/' + file_basename
                mailFiles.append(filename)
                file_to_mail_map[filename] = mail
            else:
                mail.processing_state = Mail.PROCESSING_STATES.DONE
                mail.save()
                continue
            file.close()

        # The list of sites that we wish to crawl
        num_browsers = settings.NUMBER_OF_THREADS
        sites = mailFiles
        # sites = ["file:///tmp/tmpvvfmzvpo"]
        # Loads the manager preference and 3 copies of the default browser dictionaries
        print('Starting OpenWPM to view mails.')
        manager_params, browser_params = TaskManager.load_default_params(num_browsers)

        # Update browser configuration (use this for per-browser settings)
        for i in range(num_browsers):
            # Record HTTP Requests and Responses
            browser_params[i]['http_instrument'] = True
            # Enable flash for all three browsers
            # browser_params[i]['disable_flash'] = False
            browser_params[i]['headless'] = True
            browser_params[i]['spoof_mailclient'] = True

        # Update TaskManager configuration (use this for crawl-wide settings)
        manager_params['data_directory'] = settings.OPENWPM_DATA_DIR
        manager_params['log_directory'] = settings.OPENWPM_LOG_DIR

        # Instantiates the measurement platform
        # Commands time out by default after 60 seconds
        manager = TaskManager.TaskManager(manager_params, browser_params)

        # Visits the sites in succession rotating the browsers
        for site in sites:
            print(site)
            command_sequence = CommandSequence.CommandSequence(site, reset=True)

            # Start by visiting the page
            command_sequence.get(sleep=0, timeout=settings.OPENWPM_TIMEOUT)

            # dump_profile_cookies/dump_flash_cookies closes the current tab.
            # TODO Not dumping cookies here, as they should be extractable from the response headers.
            # command_sequence.dump_profile_cookies(120)

            # index=None browsers visit sites asynchronously
            manager.execute_command_sequence(command_sequence, index=None)

        # Shuts down the browsers and waits for the data to finish logging
        manager.close()

        # Make sure the db connection is open
        connection.connect()

        print('Importing OpenWPM results.')
        failed_mails = []
        wpm_db = settings.OPENWPM_DATA_DIR + "crawl-data.sqlite"
        if os.path.isfile(wpm_db):
            conn = lite.connect(wpm_db)
            db_cursor = conn.cursor()

            for fileName in mailFiles:
                if not Mail.import_openwpmresults(fileName, file_to_mail_map[fileName], db_cursor):
                    failed_mails.append(file_to_mail_map[fileName])
                    file_to_mail_map[fileName].processing_fails = file_to_mail_map[fileName].processing_fails + 1
                    file_to_mail_map[fileName].save()
                else:
                    file_to_mail_map[fileName].processing_state = Mail.PROCESSING_STATES.VIEWED
                    file_to_mail_map[fileName].processing_fails = 0
                    file_to_mail_map[fileName].save()
                # TODO
                os.unlink('/tmp/' + fileName.split('/')[3])  # remove file to avoid zombie data
            db_cursor.close()

            # remove openwpm sqlite db to avoid waste of disk space
            if not settings.DEVELOP_ENVIRONMENT:
                os.remove(wpm_db)
        print('Done.')
        return failed_mails

    # TODO merge import openwpm results and the call openWPM functions
    @staticmethod
    def import_openwpmresults(filename, mail, db_cursor):
        num_eresources = 0

        db_cursor.execute("SELECT * from crawl_history where arguments = ? and bool_success = 1;", (filename,))
        if len(db_cursor.fetchall()) == 0:
            return False

        # scans through the sqlite database, checking for all external calls and to which they redirect
        db_cursor.execute(
            "SELECT DISTINCT h.url, h.headers, hr.headers, h.channel_id, v.site_url, r.new_channel_id, h2.url "
            "FROM http_requests as h INNER JOIN site_visits as v on h.visit_id = v.visit_id "
            "LEFT OUTER JOIN http_redirects as r on h.channel_id = r.old_channel_id "
            "LEFT OUTER JOIN http_requests as h2 on r.new_channel_id = h2.channel_id "
            "LEFT OUTER JOIN http_responses as hr on h.url = hr.url "
            "WHERE h.url not like '%favicon.ico' and site_url = ?;", (filename,))

        openWPM_entries = db_cursor.fetchall()
        num_openWpm_entries = len(openWPM_entries)
        # scans through the database, checking for all external calls
        # for url, top_url in cur.execute("SELECT DISTINCT h.url, v.site_url "
        #                                 "FROM http_requests as h JOIN site_visits as v ON "
        #                                 "h.visit_id = v.visit_id WHERE top_level_url = ?;", (filename,)):

        for url, request_headers, response_headers, channel_id, top_url, new_channel_id, redirects_to \
                in openWPM_entries:
            # check if the url has a parent and is therefore not the start of a chain.
            db_cursor.execute("select * FROM http_redirects WHERE http_redirects.new_channel_id = ?;",
                              (channel_id,))

            is_start_of_chain = False
            if db_cursor.fetchone() is None:
                is_start_of_chain = True

            # eresource is end of chain
            # TODO set the type to the type of the return headers.
            if new_channel_id is None or new_channel_id == '':
                r, created = Eresource.objects.get_or_create(type="con", request_headers=request_headers,
                                                             response_headers=response_headers,
                                                             url=url, channel_id=channel_id,
                                                             param=top_url, mail=mail,
                                                             is_start_of_chain=is_start_of_chain, is_end_of_chain=True)
            # eresource redirects to other eresource
            else:
                r, created = Eresource.objects.get_or_create(type="con", request_headers=request_headers,
                                                             response_headers=response_headers, url=url,
                                                             channel_id=channel_id,
                                                             redirects_to_channel_id=new_channel_id,
                                                             redirects_to_url=redirects_to,
                                                             param=top_url, mail=mail,
                                                             is_start_of_chain=is_start_of_chain, is_end_of_chain=False)

            # save load resources in eresource of type connection
            if created:
                mail.connect_tracker(eresource=r)
                r.save()
                num_eresources = num_eresources + 1
        print('Number of Eresources added to the Database: %s' % num_eresources)
        if (num_openWpm_entries != num_eresources):
            print('Different number of entries have been added, than the OpenWPM database returned!')
        return True

    @staticmethod
    def call_openwpm_click_links(link_mail_map):
        wpm_db = settings.OPENWPM_DATA_DIR + "crawl-data.sqlite"
        if os.path.exists(wpm_db):
            os.remove(wpm_db)

        print('Preparing data for OpenWPM.')
        sites = []
        for url in link_mail_map:
            sites.append(url)
        # The list of sites that we wish to crawl
        num_browsers = settings.NUMBER_OF_THREADS

        # Loads the manager preference and 3 copies of the default browser dictionaries
        print('Starting OpenWPM to visit links.')
        manager_params, browser_params = TaskManager.load_default_params(num_browsers)

        # Update browser configuration (use this for per-browser settings)
        for i in range(num_browsers):
            # Record HTTP Requests and Responses
            browser_params[i]['http_instrument'] = True
            # Enable flash for all three browsers
            # browser_params[i]['disable_flash'] = False
            # browser_params['js_instrument'] = True
            browser_params[i]['headless'] = True

        # Update TaskManager configuration (use this for crawl-wide settings)
        manager_params['data_directory'] = settings.OPENWPM_DATA_DIR
        manager_params['log_directory'] = settings.OPENWPM_LOG_DIR

        # Instantiates the measurement platform
        # Commands time out by default after 60 seconds
        manager = TaskManager.TaskManager(manager_params, browser_params)

        # Visits the sites in succession rotating the browsers
        for site in sites:
            command_sequence = CommandSequence.CommandSequence(site, reset=True)

            # Start by visiting the page
            command_sequence.get(sleep=0, timeout=settings.OPENWPM_TIMEOUT)

            # todo Not dumping cookies here, as they can be extracted from the response headers
            # command_sequence.dump_profile_cookies(120)

            # index=None browsers visit sites asynchronously
            manager.execute_command_sequence(command_sequence, index=None)

        # Shuts down the browsers and waits for the data to finish logging
        manager.close()

        # Make sure the db connection is open
        connection.connect()

        print('Importing OpenWPM results.')
        failed_urls = {}
        wpm_db = settings.OPENWPM_DATA_DIR + "crawl-data.sqlite"

        if os.path.isfile(wpm_db):
            conn = lite.connect(wpm_db)
            db_cursor = conn.cursor()

            for url in link_mail_map:
                if not Mail.import_openwpmresults_click(url, link_mail_map[url], db_cursor):
                    failed_urls[url] = link_mail_map[url]
                    link_mail_map[url].processing_fails = link_mail_map[url].processing_fails + 1
                    link_mail_map[url].save()
                else:
                    link_mail_map[url].processing_state = Mail.PROCESSING_STATES.LINK_CLICKED
                    link_mail_map[url].processing_fails = 0
                    link_mail_map[url].save()
            db_cursor.close()

            # remove openwpm sqlite db to avoid waste of disk space
            # if not settings.DEVELOP_ENVIRONMENT:
            #     os.remove(wpm_db)
        print('Done.')
        return failed_urls

    @staticmethod
    def import_openwpmresults_click(url, mail, db_cursor):
        num_eresources = 0
        # connect to the input database
        db_cursor.execute("SELECT * from crawl_history where arguments = ? and bool_success = 1;", (url,))
        if len(db_cursor.fetchall()) == 0:
            return False
        # scans through the sqlite database, checking for all external calls and to which they redirect
        db_cursor.execute(
            "SELECT DISTINCT h.url, h.headers, hr.headers, h.channel_id, v.site_url, r.new_channel_id, h2.url "
            "FROM http_requests as h INNER JOIN site_visits as v on h.visit_id = v.visit_id "
            "LEFT OUTER JOIN http_redirects as r on h.channel_id = r.old_channel_id "
            "LEFT OUTER JOIN http_requests as h2 on r.new_channel_id = h2.channel_id "
            "LEFT OUTER JOIN http_responses as hr on h.url = hr.url "
            "WHERE site_url = ? and h.url not like '%favicon.ico' and  h.top_level_url is null;", (url,))

        openWPM_entries = db_cursor.fetchall()
        num_openWpm_entries = len(openWPM_entries)
        # check whether the final url is from the service. If not discard this chain.
        service_url = None
        id = mail.identity.all()
        print(id)
        if id.exists():
            service_url = id[0].service.url
            for url, request_headers, response_headers, channel_id, top_url, new_channel_id, redirects_to \
                    in openWPM_entries:

                if new_channel_id is None or new_channel_id == '':
                    if service_url not in url:
                        print('Clicked link did not end on services site. Possible link to another website. Skipping.')
                        # print('service: {}'.format(service_url))
                        # print('URL: {}'.format(url))
                        # print('redirects_to: {}'.format(redirects_to))
                        return True
                    # print('Correctly ends on service domain.')
                    # print('service: {}'.format(service_url))
                    # print('URL: {}'.format(url))
                    # print('redirects_to: {}'.format(redirects_to))
        else:
            print('Mail has no associated identities.')

        for url, request_headers, response_headers, channel_id, top_url, new_channel_id, redirects_to \
                in openWPM_entries:
            # check if the url has a parent and is therefore not the start of a chain.
            db_cursor.execute("select * FROM http_redirects WHERE http_redirects.new_channel_id = ?;",
                              (channel_id,))

            is_start_of_chain = False
            if db_cursor.fetchone() is None:
                is_start_of_chain = True

            # eresource is end of chain
            if new_channel_id is None or new_channel_id == '':
                r, created = Eresource.objects.get_or_create(type="con_click", request_headers=request_headers,
                                                             response_headers=response_headers, url=url,
                                                             channel_id=channel_id,
                                                             param=top_url, mail=mail,
                                                             is_start_of_chain=is_start_of_chain, is_end_of_chain=True)
            # eresource redirects to other eresource
            else:
                r, created = Eresource.objects.get_or_create(type="con_click", request_headers=request_headers,
                                                             response_headers=response_headers, url=url,
                                                             channel_id=channel_id,
                                                             redirects_to_channel_id=new_channel_id,
                                                             redirects_to_url=redirects_to,
                                                             param=top_url, mail=mail,
                                                             is_start_of_chain=is_start_of_chain, is_end_of_chain=False)

            # save load resources in eresource of type connection
            if created:
                mail.connect_tracker(eresource=r)
                r.save()
                num_eresources = num_eresources + 1
        print('Number of Eresources added to the Database: %s' % num_eresources)
        if (num_openWpm_entries != num_eresources):
            print('Different number of entries have been added, than the OpenWPM database returned!')
            logger.error('Different number of entries have been added, than the OpenWPM database returned!')
        return True

    @staticmethod
    def connect_tracker(eresource):
        extracturl = tldextract.extract(eresource.url)
        host = "{}.{}".format(extracturl.domain, extracturl.suffix)

        # Don't save our own domain as third party.
        localDomain = tldextract.extract(settings.LOCALHOST_URL)
        localHost = "{}.{}".format(localDomain.domain, localDomain.suffix)
        if localHost in host:
            return

        thirdparty, created = Thirdparty.objects.update_or_create(name=host, host=host,
                                                                  defaults={'resultsdirty': True}, )
        eresource.host = thirdparty
        eresource.save()

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
        return self.first_third_party_by_type('a')

    @cached_property
    def first_third_party_connections(self):
        return self.first_third_party_by_type('con')

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
        return first_party, first_party_personalized, third_party, third_party_personalized


class Eresource(models.Model):
    RESOURCE_TYPES = (
        ('a', 'Link'),
        ('img', 'Image'),
        ('con', 'Connection')
    )
    type = models.CharField(max_length=50, choices=RESOURCE_TYPES)
    url = models.TextField(max_length=2000, null=True, blank=True)
    # the http channel id of OpenWPM for identification
    channel_id = models.CharField(max_length=255, null=True, blank=True)
    param = models.TextField(max_length=2000, null=True, blank=True)
    request_headers = models.TextField(max_length=3000, null=True, blank=True)
    response_headers = models.TextField(max_length=3000, null=True, blank=True)
    mail = models.ForeignKey(Mail, on_delete=models.CASCADE)
    host = models.ForeignKey('Thirdparty', null=True, on_delete=models.SET_NULL)
    diff_eresource = models.ForeignKey('self', related_name='diff', on_delete=models.SET_NULL, null=True)
    mail_leakage = models.TextField(null=True, blank=True)
    personalised = models.BooleanField(default=False)
    # the eresource this one redirects to
    redirects_to = models.ForeignKey('self', related_name='redirect', on_delete=models.CASCADE, null=True)
    # the url of the eresource this one redirects to
    redirects_to_url = models.CharField(max_length=2000, null=True, blank=True)
    # the channelID of the eresource this one connects to
    redirects_to_channel_id = models.CharField(max_length=255, null=True, blank=True)
    is_end_of_chain = models.BooleanField(default=True)
    is_start_of_chain = models.BooleanField(default=True)
    possible_unsub_link = models.BooleanField(default=False)

    def __str__(self):
        return "({})|{}".format(self.type, self.url)

    @classmethod
    def create_clickable(cls, link, possible_unsubscribe_link, mail):
        r, created = Eresource.objects.get_or_create(type="a", url=link["href"],
                                                     possible_unsub_link=possible_unsubscribe_link,
                                                     param=str(link.attrs) + str(link.contents),
                                                     mail=mail)
        if created:
            mail.connect_tracker(eresource=r)
            r.save()

    @classmethod
    def create_static_eresource(cls, element, source_string, mail, possible_unsubscribe_link=False):
        if 'http' not in element[source_string] or element[source_string] is None:
            return
        element[source_string] = ''.join(element[source_string].split())
        r, created = Eresource.objects.get_or_create(type=element.name, url=element[source_string],
                                                     possible_unsub_link=possible_unsubscribe_link,
                                                     param=str(element.attrs) + str(element.contents),
                                                     mail=mail)
        if created:
            mail.connect_tracker(eresource=r)
            r.save()

    @property
    def personalized(self):
        if self.diff_eresource:
            return True
        return False

    @staticmethod
    def is_unsub_word_in_link(link):
        if 'http' not in link['href']:
            return False
        for unsub_word in settings.UNSUBSCRIBE_LINK_DICT:
            if unsub_word in link["href"].casefold() or unsub_word in link.text.casefold():
                # print('Found possible unsubscribe link: %s' % link)
                return True
            try:
                if unsub_word in link['alias'].casefold():
                    # print('Found possible unsubscribe link: %s' % link)
                    return True
            except KeyError:
                continue
        return False


class Thirdparty(models.Model):
    name = models.CharField(max_length=200, null=False, blank=False)
    host = models.CharField(max_length=200, null=False, blank=False, unique=True)
    resultsdirty = models.BooleanField(default=True)

    def __str__(self):
        return "({})|{}".format(self.name, self.host)

    def derive_thirdparty_cache_path(self):
        return 'frontend.ThirdPartyView.result.' + str(self.id) + ".site_params"

# class RequestChain(models.Model):
#     mail = models.ForeignKey(Mail, on_delete=models.CASCADE)
#     host = models.ForeignKey('Trackhosts', null=True, on_delete=models.SET_NULL)
