import logging
from django.conf import settings
from django.db import models

logger = logging.getLogger(__name__)


class Eresource(models.Model):
    RESOURCE_TYPES = (
        ("a", "Link"),
        ("img", "Image"),
        ("con", "Connection"),
        ("con_click", "Connection_clicked"),
        ("link", "css"),
        ("script", "JavaScript"),
    )
    type = models.CharField(max_length=50, choices=RESOURCE_TYPES)
    url = models.TextField(max_length=2000, null=True, blank=True)
    # the http channel id of OpenWPM for identification
    channel_id = models.CharField(max_length=255, null=True, blank=True)
    param = models.TextField(max_length=2000, null=True, blank=True)
    request_headers = models.TextField(max_length=3000, null=True, blank=True)
    response_headers = models.TextField(max_length=3000, null=True, blank=True)
    mail = models.ForeignKey("Mail", on_delete=models.CASCADE)
    host = models.ForeignKey("Thirdparty", null=True, on_delete=models.SET_NULL)
    diff_eresource = models.ForeignKey(
        "self", related_name="diff", on_delete=models.SET_NULL, null=True
    )
    mail_leakage = models.TextField(null=True, blank=True)
    personalised = models.BooleanField(default=False)
    # the eresource this one redirects to
    redirects_to = models.ForeignKey(
        "self", related_name="redirect", on_delete=models.CASCADE, null=True
    )
    # the url of the eresource this one redirects to
    redirects_to_url = models.CharField(max_length=2000, null=True, blank=True)
    # the channelID of the eresource this one connects to
    redirects_to_channel_id = models.CharField(max_length=255, null=True, blank=True)
    is_end_of_chain = models.BooleanField(default=True)
    is_start_of_chain = models.BooleanField(default=True)
    possible_unsub_link = models.BooleanField(default=False)

    class Meta:
        indexes = [models.Index(fields=['mail', 'type', 'personalised']),]

    def __str__(self):
        return "({})|{}".format(self.type, self.url)

    @classmethod
    def create_clickable(cls, link, possible_unsubscribe_link, mail):
        r, created = Eresource.objects.get_or_create(
            type="a",
            url=link["href"],
            possible_unsub_link=possible_unsubscribe_link,
            param=str(link.attrs) + str(link.contents),
            mail=mail,
        )
        if created:
            mail.connect_tracker(eresource=r)

    @classmethod
    def create_static_eresource(
        cls, element, source_string, mail, possible_unsubscribe_link=False
    ):
        element_string = str(element)
        if "javascript" in element_string:
            mail.contains_javascript = True
        try:
            if "http" not in element[source_string] or element[source_string] is None:
                return
        except KeyError:
            return
        element[source_string] = "".join(element[source_string].split())
        r, created = Eresource.objects.get_or_create(
            type=element.name,
            url=element[source_string],
            possible_unsub_link=possible_unsubscribe_link,
            param=str(element.attrs) + str(element.contents),
            mail=mail,
        )
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
        if "http" not in link["href"]:
            return False
        for unsub_word in settings.UNSUBSCRIBE_LINK_DICT:
            if (
                unsub_word in link["href"].casefold()
                or unsub_word in link.text.casefold()
            ):
                # print('Found possible unsubscribe link: %s' % link)
                return True
            try:
                if unsub_word in link["alias"].casefold():
                    # print('Found possible unsubscribe link: %s' % link)
                    return True
            except KeyError:
                continue
        return False
