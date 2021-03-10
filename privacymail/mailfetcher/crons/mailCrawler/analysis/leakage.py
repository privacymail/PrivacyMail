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


def analyze_single_mail_for_leakage(h_x_original_to, eresources):
    hashdict = Mail.generate_match_dict(h_x_original_to)
    print(hashdict)
    for eresource in eresources:
        analyze_eresource(eresource, hashdict)
    return eresources


def analyze_eresource(eresource, hashdict):
    for key, val in hashdict.items():
        if (
            str(val) in eresource["url"]
            or str(val).casefold() in eresource["url"].replace("-", "").casefold()
        ):
            print("leakage")
            if eresource["mail_leakage"] is None or eresource["mail"] == "":
                eresource["mail_leakage"] = key
            else:
                if key in eresource["mail_leakage"]:
                    continue
                eresource["mail_leakage"] = eresource["mail_leakage"] + ", " + key