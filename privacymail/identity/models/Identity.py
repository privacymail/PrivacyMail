import random

import names
from django.apps import apps
from django.contrib.postgres.fields import ArrayField
from django.core import exceptions
from django.db import models
from django_countries.fields import CountryField
from identity.util import convertForJsonResponse
from model_utils import Choices


class Identity(models.Model):
    first_name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    mail = models.EmailField(unique=True)
    gender = models.BooleanField()  # True is male
    service = models.ForeignKey("Service", on_delete=models.SET_NULL, null=True)
    approved = models.BooleanField(default=False)
    lastapprovalremindersend = models.TimeField(default=None, null=True)
    receives_third_party_spam = models.BooleanField(default=False)
    is_dead = models.BooleanField(default=True)

    @classmethod
    def create(cls, service, domain):
        def gen_name(gender):
            if gender:  # if male
                first_name = names.get_first_name(gender="male")
            else:
                first_name = names.get_first_name(gender="female")
            surname = names.get_last_name()
            return (first_name, surname)

        i = cls(service=service)
        # Generate random gender and name
        i.gender = bool(random.getrandbits(1))

        # Keep generating names until we find a pair that is not yet taken
        while True:
            first_name, surname = gen_name(i.gender)
            if not Identity.objects.filter(
                first_name=first_name, surname=surname
            ).exists():
                break

        i.first_name = first_name
        i.surname = surname
        i.mail = "{}.{}@{}".format(i.first_name, i.surname, domain).lower()

        i.save()
        return i

    def mark_as_dead (self):
        if not self.is_dead:
            self.is_dead = True
            self.save()

    def resurrect (self):

        if self.is_dead:
            self.is_dead = False
            self.save()

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
