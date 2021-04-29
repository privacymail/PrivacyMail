import random

import names
from django.apps import apps
from django.contrib.postgres.fields import ArrayField
from django.core import exceptions
from django.db import models
from django_countries.fields import CountryField
from identity.util import convertForJsonResponse
from identity.models import Service
from model_utils import Choices


class ServiceThirdPartyEmbeds(models.Model):
    STATIC = "STATIC"
    ONVIEW = "ONVIEW"
    ONCLICK = "ONCLICK"
    UNDETERMINED = "UNDETERMINED"

    EMBED_TYPES = Choices(
        (STATIC, "static"),
        (ONVIEW, "onView"),
        (ONCLICK, "onClick"),
        (UNDETERMINED, "undetermined"),
    )

    service = models.ForeignKey(
        Service, related_name="embeds", on_delete=models.SET_NULL, null=True
    )
    thirdparty = models.ForeignKey(
        "mailfetcher.Thirdparty",
        related_name="embeds",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    leaks_address = models.BooleanField(default=False)
    embed_type = models.CharField(
        choices=EMBED_TYPES, default=EMBED_TYPES.UNDETERMINED, max_length=20
    )
    mail = models.ForeignKey("mailfetcher.Mail", on_delete=models.CASCADE, null=True)
    sets_cookie = models.BooleanField(default=False)
    receives_identifier = models.BooleanField(default=False)

    def toJSON(self):
        return {
            "service": convertForJsonResponse(self.service),
            "thirdparty": convertForJsonResponse(self.thirdparty),
            "leaks_address": convertForJsonResponse(self.leaks_address),
            "embed_type": convertForJsonResponse(self.embed_type),
            "mail": convertForJsonResponse(self.mail),
            "sets_cookie": convertForJsonResponse(self.sets_cookie),
            "receives_identifier": convertForJsonResponse(self.receives_identifier),
        }
