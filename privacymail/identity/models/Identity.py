import random
import names

from django.db import models
from identity.util import convertForJsonResponse
from mailfetcher.crons.mailCrawler.confirmMail import approve_from_mail


class Identity(models.Model):
    first_name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    mail = models.EmailField(unique=True)
    gender = models.BooleanField()  # True is male
    service = models.ForeignKey("Service",
                                on_delete=models.SET_NULL,
                                null=True)
    approved = models.BooleanField(default=False)
    lastapprovalremindersend = models.TimeField(default=None, null=True)
    receives_third_party_spam = models.BooleanField(default=False)

    @classmethod
    def create(cls, service, domain):
        def gen_name(gender):
            gender_name = "male" if gender else "female"

            first_name = names.get_first_name(gender=gender_name)
            surname = names.get_last_name()
            return (first_name, surname)

        i = cls(service=service)
        # Generate random gender and name
        i.gender = bool(random.getrandbits(1))

        # Keep generating names until we find a pair that is not yet taken
        while True:
            first_name, surname = gen_name(i.gender)
            if not Identity.objects.filter(first_name=first_name,
                                           surname=surname).exists():
                break

        i.first_name = first_name
        i.surname = surname
        i.mail = "{}.{}@{}".format(i.first_name, i.surname, domain).lower()

        i.save()
        return i

    def toJSON(self):
        return {
            "first_name": convertForJsonResponse(self.first_name),
            "surname": convertForJsonResponse(self.surname),
            "mail": convertForJsonResponse(self.mail),
            "gender": convertForJsonResponse(self.gender),
            "service": convertForJsonResponse(self.service),
            "approved": convertForJsonResponse(self.approved),
        }

    def __str__(self):
        return self.mail

    def try_auto_approve(self, mail):
        '''
        Tries to auto approve an identity with a given email.

        Returns whether the approve was successfull or not.
        '''
        if self.approved:
            return False

        first_mail = self.message.order_by('date_time').first()
        if first_mail and first_mail.id == mail.id:
            if mail.body_html:
                approved = approve_from_mail(mail)
                if approved:
                    self.approved = True
                    self.save()
                    return True
            else:
                return False
        return False
