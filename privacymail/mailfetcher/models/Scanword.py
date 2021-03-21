import logging
from django.db import models

logger = logging.getLogger(__name__)


class Scanword(models.Model):
    type = models.CharField(max_length=50)
    word = models.TextField(max_length=2000)

    def __str__(self):
        return f"({self.type}): {self.word}"
