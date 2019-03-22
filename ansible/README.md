# Deployment instructions

Deploying PrivacyMail is fairly simple. You need a server running a recent version of Ubuntu Server (tested with 18.04 LTS) that permits SSH login as root. Configure this host in your ansible inventory and set the correct target in the deploy.yml.

To allow pulling from the repository, you currently need a deploy key set up. Put the private key into files/id_deploy (make sure the key does not require a passphrase).

We use the Ansible passwordstore lookup to store sensitive information such as keys and passwords. Ensure the relevant keys from templates/settings.py are in your local pass utility:

- Database:
  - privacymail/postgres-user
  - privacymail/postgres-password
- Unix:
  - privacymail/privacymail-user-pass
- Django:
  - privacymail/django-secret-key
  - privacymail/raven-dsn
  - privacymail/admin/contacts
  - privacymail/admin/send-user
  - privacymail/admin/send-pass
- Email accounts:
  - privacymail/email/newsletterme/user
  - privacymail/email/newsletterme/pass
  - privacymail/email/privacyletter/user
  - privacymail/email/privacyletter/pass
  - privacymail/email/privacy-mail/user
  - privacymail/email/privacy-mail/pass

Check templates/settings.py and the deploy.yml for the meaning of all of these values, and set them accordingly in your local `pass` utility.

Afterwards, you should be able to run `ansible-playbook deploy.yml` to get a fully featured copy of PrivacyMail set up. The site will be served on port 80, and does not support TLS by default - if you want to expose it on the internet, please add TLS support etc., however, we decided against making this part of the standard setup, as it is overkill for local debugging installations, and may break more complex setups (e.g. those using proxies).

Also note that we currently do not install the processing cronjobs, as they may cause problems on our setup. For production use, do not forget to install the cronjobs as required. More information on this will be added here eventually.