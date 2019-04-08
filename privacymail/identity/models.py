from django.db import models
from django.core import exceptions
import names
import random
from django.apps import apps
from model_utils import Choices
from django_countries.fields import CountryField


# Create your models here.
class Identity(models.Model):
    first_name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    mail = models.EmailField(unique=True)
    gender = models.BooleanField()  # True is male
    service = models.ForeignKey("Service", on_delete=models.SET_NULL, null=True)
    approved = models.BooleanField(default=False)
    lastapprovalremindersend = models.TimeField(default=None, null=True)
    receives_third_party_spam = models.BooleanField(default=False)

    @classmethod
    def create(cls, service, domain):
        i = cls(service=service)
        # Generate random gender and name
        i.gender = bool(random.getrandbits(1))
        if i.gender:  # if male
            i.first_name = names.get_first_name(gender='male')
        else:
            i.first_name = names.get_first_name(gender='female')
        i.surname = names.get_last_name()

        # A lot of random names can be generated. Therefor we expect the mail to be unique
        # TODO Ensure that name is not already taken
        i.mail = "{}.{}@{}".format(i.first_name, i.surname, domain).lower()
        i.save()
        return i

    def __str__(self):
        return self.mail


class Service(models.Model):
    ADULT = "adult"
    ART = "art"
    ADVERTISING = "ads"
    GAMES = "games"
    ENTERTAINMENT = "entertainment"
    HEALTH = "health"
    FINANCE = "finance"
    NEWS = "news"
    SHOPPING = "shopping"
    B2B = "b2b"
    REFERENCE = "reference"
    SCIENCE = "science"
    POLITICS = "politics"
    ACTIVIST = "activist"
    SPORTS = "sports"
    TRAVEL = "travel"
    UNKNOWN = "unknown"

    SECTOR_CHOICES = ((ACTIVIST, "Activist"),
                      (ADULT, "Adult"),
                      (ADVERTISING, "Advertising"),
                      (ART, "Art"),
                      (B2B, "Business-to-Business"),
                      (ENTERTAINMENT, "Entertainment"),
                      (FINANCE, "Financial"),
                      (GAMES, "Games"),
                      (HEALTH, "Health"),
                      (NEWS, "News"),
                      (POLITICS, "Political Party / Politician"),
                      (REFERENCE, "Reference"),
                      (SCIENCE, "Science"),
                      (SHOPPING, "Shopping"),
                      (SPORTS, "Sports"),
                      (TRAVEL, "Travel"),
                      (UNKNOWN, "Unknown"))

    url = models.CharField(max_length=255)  # should not contain http, because mailfetcher.check_for_unusual_sender uses this value to map sender domain
    name = models.CharField(max_length=50)
    thirdparties = models.ManyToManyField('mailfetcher.Thirdparty', through='ServiceThirdPartyEmbeds',
                                          related_name='services')
    resultsdirty = models.BooleanField(default=True)
    hasApprovedIdentity = models.BooleanField(default=False)

    country_of_origin = CountryField(blank_label='(select country)', blank=True)
    sector = models.CharField(choices=SECTOR_CHOICES, max_length=30, default=UNKNOWN)

    def __str__(self):
        return self.name

    @classmethod
    def create(cls, url, name):
        # Create the service
        i = cls(url=url, name=name)
        i.save()
        # Check if the service already exists as a third party
        try:
            tp = apps.get_model('mailfetcher', 'Thirdparty').objects.get(host=url)
            print("Found third party")
            # Third party found, set service foreign key and save
            tp.service = i
            tp.save()
            # Check if the third party already has a country of origin associated with it
            if tp.country_of_origin:
                # Country defined, take over metadata for the newly created service
                i.country_of_origin = tp.country_of_origin
                i.save()
        except exceptions.ObjectDoesNotExist:
            # Not yet a known third party host, ignore
            pass
        return i

    @classmethod
    def get_or_create(cls, url, name):
        cls._for_write = True
        try:
            return (cls.objects.get(url=url, name=name), False)
        except exceptions.ObjectDoesNotExist:
            return (cls.create(url=url, name=name), True)

    def set_has_approved_identity(self):
        if self.hasApprovedIdentity:
            return
        for identity in self.identity_set.all():
            if identity.approved:
                self.hasApprovedIdentity = True
                self.save()

    def mails(self):
        Mail = apps.get_model('mailfetcher', 'Mail')
        return Mail.objects.filter(identity__service=self, identity__approved=True)
        # return Mail.objects.filter(identity__service=self)

    # calculate the avererage by Eresource type
    def avg(self, type):
        first_party_sum = 0
        first_party_personalized_sum = 0
        third_party_sum = 0
        third_party_personalized_sum = 0

        for mail in self.mails():
            first_party, first_party_personalized, third_party, third_party_personalized = mail.first_third_party_by_type(type)

            first_party_personalized_sum += first_party_personalized
            first_party_sum += first_party
            third_party_personalized_sum += third_party_personalized
            third_party_sum += third_party

        n = self.mails().count()
        n_double = self.mails().exclude(mail_from_another_identity=None).count()
        if n == 0:
            return None
        if n_double == 0:
            return first_party_sum / n, None, \
                   third_party_sum / n, None
        return first_party_sum / n, \
               first_party_personalized_sum / n_double, \
               third_party_sum / n, \
               third_party_personalized_sum / n_double

    def derive_service_cache_path(self):
        return 'frontend.ServiceView.result.' + str(self.id) + ".site_params"


class ServiceThirdPartyEmbeds(models.Model):
    STATIC = 'STATIC'
    ONVIEW = 'ONVIEW'
    ONCLICK = 'ONCLICK'
    UNDETERMINED = 'UNDETERMINED'

    EMBED_TYPES = Choices(
        ('STATIC', 'static'),
        ('ONVIEW', 'onView'),
        ('ONCLICK', 'onClick'),
        ('UNDETERMINED', 'undetermined')
    )

    service = models.ForeignKey(Service, related_name='embeds', on_delete=models.SET_NULL, null=True)
    thirdparty = models.ForeignKey('mailfetcher.Thirdparty', related_name='embeds', on_delete=models.SET_NULL,
                                   null=True, blank=True)
    leaks_address = models.BooleanField(default=False)
    embed_type = models.CharField(choices=EMBED_TYPES, default=EMBED_TYPES.UNDETERMINED, max_length=20)
    mail = models.ForeignKey('mailfetcher.Mail', on_delete=models.CASCADE, null=True)
    sets_cookie = models.BooleanField(default=False)
    receives_identifier = models.BooleanField(default=False)
