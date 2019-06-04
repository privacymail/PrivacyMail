from django.core.management.base import BaseCommand, CommandError
from identity.models import Service
from mailfetcher.models import Mail, Eresource
from datetime import datetime
import sys


class Command(BaseCommand):
    def query_yes_no(self, question, default="no"):
        """Ask a yes/no question via raw_input() and return their answer.

        "question" is a string that is presented to the user.
        "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

        The "answer" return value is True for "yes" or False for "no".
        """
        valid = {"yes": True, "y": True, "ye": True,
                 "no": False, "n": False}
        if default is None:
            prompt = " [y/n] "
        elif default == "yes":
            prompt = " [Y/n] "
        elif default == "no":
            prompt = " [y/N] "
        else:
            raise ValueError("invalid default answer: '%s'" % default)

        while True:
            sys.stdout.write(question + prompt)
            choice = input().lower()
            if default is not None and choice == '':
                return valid[default]
            elif choice in valid:
                return valid[choice]
            else:
                sys.stdout.write("Please respond with 'yes' or 'no' "
                                 "(or 'y' or 'n').\n")

    def add_arguments(self, parser):
        parser.add_argument('--all', action="store_true", dest="recrawl_all", help="Mark all messages for recrawling. Cannot be used in combination with --service or --newer-than")
        parser.add_argument('--service', type=int, dest="sid", help="Only mark messages belonging to the specified service ID for recrawling. Can be combined with --newer-than.")
        parser.add_argument('--newer-than', dest="newer_than", help="Only mark messages more recent than the provided date for recrawling. Date format: YYYY-MM-DD. Can be combined with --service.")

    def handle(self, *args, **options):
        if options['newer_than']:
            try:
                dt = datetime.strptime(options['newer_than'], '%Y-%m-%d')
            except ValueError:
                raise CommandError("That is not a valid date")
            if options['sid']:
                service = Service.objects.get(pk=options['sid'])
                mails = Mail.objects.filter(date_time__range=[dt, datetime.now()], identity__service=service)
                print("Selecting mails by service %s (%s) newer than %s" % (service.pk, service.name, datetime.strftime(dt, '%B %d, %Y')))
            else:
                mails = Mail.objects.filter(date_time__range=[dt, datetime.now()])
                print("Selecting mails newer than", datetime.strftime(dt, '%B %d, %Y'))

        elif options['sid']:
            if options['recrawl_all']:
                raise CommandError("Cannot use both --all and --service")

            service = Service.objects.get(pk=options['sid'])
            print("Selecting Mails belonging to service %s (%s)" % (service.pk, service.name))
            mails = Mail.objects.filter(identity__service=service)

        elif options['recrawl_all']:
            mails = Mail.objects.all()

        else:
            raise CommandError("Must specify --service, --all, or --newer-than to designate targets for recrawl. See --help for details.")

        print("Found", mails.count(), "matching emails.")

        # The following operations will delete stuff from the database. Make sure that the user is aware of this.
        print("###############################")
        print("#  ! ! ! W A R N I N G ! ! !  #")
        print("###############################")
        print("This is a destructive operation that can lead to loss of data. Only proceed if you know exactly what this function is doing.")
        if not self.query_yes_no("Do you want to proceed?", default="no"):
            print("Aborting.")
            return

        # Actually perform the operation on the Mails:
        # TODO Do we also need to deal with any third party references etc.? Double-check
        print("Deleting associated eresources.")
        for mail in mails:
            # Delete existing eresources
            Eresource.objects.filter(mail=mail).delete()

        # Mark mails for recrawl
        print("Marking Messages for recrawl.")
        mails.update(processing_state=Mail.PROCESSING_STATES.UNPROCESSED, processing_fails=0, contains_javascript=False, possible_AB_testing=False)
        print("Done.")
