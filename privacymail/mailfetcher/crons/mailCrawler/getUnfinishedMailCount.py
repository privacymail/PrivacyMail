from mailfetcher.models import Mail

from django.conf import settings

# Check whether there are too many mail in the database waiting to be processed.
def getUnfinishedMailCount():
    viewed_mails = (
        Mail.objects.filter(processing_state=Mail.PROCESSING_STATES.VIEWED)
        .exclude(processing_fails__gte=settings.OPENWPM_RETRIES)
        .count()
    )
    clicked_mails = (
        Mail.objects.filter(processing_state=Mail.PROCESSING_STATES.LINK_CLICKED)
        .exclude(processing_fails__gte=settings.OPENWPM_RETRIES)
        .count()
    )
    unprocessed_mails = (
        Mail.objects.filter(processing_state=Mail.PROCESSING_STATES.UNPROCESSED)
        .exclude(processing_fails__gte=settings.OPENWPM_RETRIES)
        .count()
    )
    failed_mails = Mail.objects.filter(
        processing_fails__gte=settings.OPENWPM_RETRIES
    ).count()

    unfinished_mail_count = viewed_mails + clicked_mails + unprocessed_mails

    print(
        "{} unprocessed mails in database. Additional {} mails are in failed state".format(
            unfinished_mail_count, failed_mails
        )
    )
    print(
        "{} unprocessed, {} viewed and {} link_clicked.".format(
            unprocessed_mails, viewed_mails, clicked_mails
        )
    )

    return unfinished_mail_count