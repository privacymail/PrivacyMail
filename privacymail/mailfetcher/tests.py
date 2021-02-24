from django.test import TestCase
from mailfetcher.models import Mail
from identity.models import Identity, Service
import email


class AutoConfirm(TestCase):
    def setUp(self):
        """
        create a service and a identity
        """
        service = Service.create('nbcnews.com', 'NBCNews')
        identity = Identity.create(service, 'newsletterme.de')
        identity.surname = "cartier"
        identity.first_name = "cathy"
        identity.mail = 'cathy.cartier@newsletterme.de'
        identity.save()

    def test_auto_approval(self):
        mail = b''
        with open('./mailfetcher/testdata/mail_approvable.eml', 'rb') as f:
            mail = f.read()

        mail = Mail.create(email.message_from_bytes(mail))

        self.assertIsNotNone(mail)
        self.assertTrue(mail.identity.first().approved)

    def test_no_approval(self):
        mail = b''
        with open('./mailfetcher/testdata/mail_unapprovable.eml', 'rb') as f:
            mail = f.read()

        mail = Mail.create(email.message_from_bytes(mail))

        self.assertIsNotNone(mail)
        self.assertFalse(mail.identity.first().approved)

    def test_second_mail_no_approval(self):
        mail1 = b''
        with open('./mailfetcher/testdata/mail_unapprovable.eml', 'rb') as f:
            mail1 = f.read()

        mail1 = Mail.create(email.message_from_bytes(mail1))

        mail2 = b''
        with open('./mailfetcher/testdata/mail_approvable.eml', 'rb') as f:
            mail2 = f.read()

        mail2 = Mail.create(email.message_from_bytes(mail2))

        self.assertIsNotNone(mail1)
        self.assertIsNotNone(mail2)
        self.assertFalse(mail2.identity.first().approved)
