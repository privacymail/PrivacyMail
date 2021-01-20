from mailfetcher.models import Mail, Eresource


def analyze_mail_connections_for_leakage(mail):
    hashdict = None

    all_eresources = Eresource.objects.filter(mail=mail).exclude(
        possible_unsub_link=True
    )
    if mail.h_x_original_to is None:
        print("Did not find mailaddress. Mail: {}".format(mail))
        return
    hashdict = Mail.generate_match_dict(mail.h_x_original_to)
    for eresource in all_eresources:
        Mail.analyze_eresource(eresource, hashdict)