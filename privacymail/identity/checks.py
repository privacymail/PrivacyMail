from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy
import logging
from identity.models import ServiceThirdPartyEmbeds
from identity.templatetags.tags import DetailItem

# Get named logger
logger = logging.getLogger(__name__)

STATUS_GOOD = "good"
STATUS_NEUTRAL = "neutral"
STATUS_BAD = "bad"
STATUS_CRITICAL = "critical"
RELIABILITY_RELIABLE = "reliable"
RELIABILITY_UNRELIABLE = "unreliable"


# Icon definitions
ICON_LEAK = {"icon": "fa-tint", "tooltip": _("Receives Email leak")}
ICON_FIRSTPARTY = {"icon": "fa-home", "tooltip": _("Sends the Newsletter")}


class Check():
    """Template for all checks, subclass this to create new checks, then add the
    class to SERVICE_CHECKS or EMBED_CHECKS below.

    The best strategy is to set all of these values in the constructor of the class.
    The frontend code will call the getter functions to receive the data to display.
    Please do not forget to use gettext / _('string') for localization support."""
    # ID of the check - must be unique!
    check_id = -1
    # Title of the check
    check_title = ""
    # Description
    check_description = ""
    # What is needed to pass this check?
    check_condition = ""
    # What is the result? good, neutral, bad, critical?
    check_status = ""
    # Written interpretation of result
    check_interpretation = ""
    # Under which conditions can this scan produce incorrect results?
    check_error = ""
    # How reliable are the results?
    check_reliability = ""
    # Any additional data that should be displayed (e.g. included third parties, ...)
    # Return a list of things that render well when put into the frontend. This can be
    # strings, but also models that have a rendering function. Set to None if not used.
    check_additional_data = None
    # Should this check be displayed? (Some checks may want to be hidden in specific situations)
    display = False

    def __init__(self):
        # We don't want people to use the base class, ever
        raise AssertionError("Never initialize this class directly, always use a subclass!")

    def get_id(self):
        return self.check_id

    def get_title(self):
        return self.check_title

    def get_description(self):
        return self.check_description

    def get_reliability(self):
        return self.check_reliability

    def get_status(self):
        return self.check_status

    def get_interpretation(self):
        return self.check_interpretation

    def get_condition(self):
        return self.check_condition

    def get_error(self):
        return self.check_error

    def get_additional_data(self):
        return self.check_additional_data

    def should_display(self):
        return self.display

    def is_sane(self):
        """Ensure that the check is initialized properly"""
        assert self.get_title() != ""
        assert self.get_description() != ""
        assert self.get_reliability() in (RELIABILITY_RELIABLE, RELIABILITY_UNRELIABLE)
        assert self.get_status() in (STATUS_GOOD, STATUS_BAD, STATUS_CRITICAL, STATUS_NEUTRAL)
        assert self.get_interpretation() != ""
        assert self.get_condition() != ""
        assert self.get_error() != ""
        return True


class ServiceThirdPartySpamCheck(Check):
    """Checks if suspected spam was received from third parties."""
    check_id = 1
    # Title of the check
    check_title = _("Third party spam")
    # Description
    check_description = _("Service providers may intentionally or unintentionally disclose your eMail address to third parties, including spammers. We try to detect this by tracking if identities associated with this service start receiving eMails from other senders.")
    # What is needed to pass this check?
    check_condition = _("This check fails if a mail arrives from another domain than the domain of the service and the admin manually marked it as spam.")
    # Errors
    check_error = _('Due to admin supervision this check should not create errors.')
    # Reliability
    check_reliability = RELIABILITY_RELIABLE

    def __init__(self, site_data):
        if "third_party_spam" not in site_data:
            logger.error("ServiceThirdPartySpamCheck: Missing key in cache")
            self.display = False
            return None
        tps = site_data["third_party_spam"]
        if tps == 0:
            self.check_interpretation = _("No third party spam was detected.")
            self.check_status = STATUS_GOOD
        else:
            self.check_interpretation = ungettext_lazy("%(count)d identity received third party messages.",
                                                       "%(count)d identities received third party messages.",
                                                       tps) % {'count': tps}
            self.check_status = STATUS_BAD
        self.display = True


class ServiceOnViewConnectionCheck(Check):
    """Check if third party services are contacted when opening the message."""
    check_id = 3
    check_title = _("External connections when opening the Mail")
    check_description = _("Newsletters may contain resources that are dynamically loaded from either the service provider or other websites, allowing them to track when you open the eMail. This check detects the presence of these external resources.")
    check_condition = _("This check passes if no connections are established when opening the Mail.")
    check_error = _("This check should not create errors.")
    check_reliability = RELIABILITY_RELIABLE

    def __init__(self, site_data):
        if "third_parties" not in site_data:
            logger.error("ServiceOnViewConnectionCheck: Missing third_parties in cache.")
            self.display = False
            return None
        parties = site_data["third_parties"]
        load_parties = []
        for party in parties.keys():
            if ServiceThirdPartyEmbeds.ONVIEW not in parties[party]["embed_as"]:
                # This 3rd party is not included when opening the eMail, skip it
                continue
            icons = []
            properties = []
            if parties[party]["address_leak_view"]:
                # Add a leak icon
                icons.append(ICON_LEAK)
            if party.name == site_data["service"].name:
                # Connections to the first party
                properties.append("first-party")
                icons.append(ICON_FIRSTPARTY)
            load_parties.append(DetailItem(party.name, "#", icons=icons, properties=properties))

        # Include the detected third parties as additional data
        self.check_additional_data = load_parties

        # Set status
        if len(self.check_additional_data) > 0:
            # TODO Potentially set to critical if eMail is leaked?
            self.check_status = STATUS_BAD
            self.check_interpretation = ungettext_lazy("%(count)d domain is contacted when viewing the mail with remote content enabled.",
                                                       "%(count)d domains are contacted when viewing the mail with remote content enabled.",
                                                       len(self.check_additional_data)) % {'count': len(self.check_additional_data)}
        else:
            self.check_status = STATUS_GOOD
            self.check_interpretation = _("No external domains are contacted when viewing the mail.")
        self.display = True


class ServiceOnClickThirdPartyConnectionCheck(Check):
    """Check if third party services are contacted when clicking a link in the message."""
    check_id = 4
    check_title = _("Third party connections when clicking a link")
    check_description = _("Links in the eMail may initially point to third party services such as trackers, which will forward the user to the correct address later. This check detects this kind of tracking behavior.")
    check_condition = _("This check passes if no connections to third parties are established when clicking links from the Mail.")
    check_error = _("The clicked link from the mail is determined randomly, thus some third parties may be missed.")
    check_reliability = RELIABILITY_UNRELIABLE

    def __init__(self, site_data):
        if "third_parties" not in site_data:
            logger.error("ServiceOnClickThirdPartyConnectionCheck: Missing third_parties in cache.")
            self.display = False
            return None

        parties = site_data["third_parties"]
        load_parties = []
        for party in parties.keys():
            if ServiceThirdPartyEmbeds.ONCLICK not in parties[party]["embed_as"]:
                # This 3rd party is not included when opening the eMail, skip it
                continue
            if party.name == site_data["service"].name:
                # Connections to the service itself are expected
                continue
            icons = []
            if parties[party]["address_leak_click"]:
                # Add a leak icon
                icons.append(ICON_LEAK)
            load_parties.append(DetailItem(party.name, "#", icons=icons))

        # Include the detected third parties as additional data
        self.check_additional_data = load_parties

        # Set status
        if len(self.check_additional_data) > 0:
            # TODO Potentially set to critical if eMail is leaked?
            self.check_status = STATUS_BAD
            self.check_interpretation = ungettext_lazy("%(count)d third party is contacted when clicking a link.",
                                                       "%(count)d third parties are contacted when clicking a link.",
                                                       len(self.check_additional_data)) % {'count': len(self.check_additional_data)}
        else:
            self.check_status = STATUS_GOOD
            self.check_interpretation = _("No third parties are contacted when clicking a link.")
        self.display = True


# ------------
# Embed Checks
# ------------
class EmbedOnViewConnectionCheck(Check):
    """Check if third party services are contacted when opening the message."""
    check_id = 5
    check_title = _("Contacted on view")
    check_description = _("If this domain is contacted when opening a newsletter, it may be able to track who is reading the newsletter and when they are doing it.")
    check_condition = _("This check passes if the website is never contacted when newsletters are opened.")
    check_error = _("This check should not create errors.")
    check_reliability = RELIABILITY_RELIABLE

    def __init__(self, site_data):
        if "services" not in site_data:
            logger.error("EmbedOnViewConnectionCheck: Missing services in cache.")
            self.display = False
            return None
        parties = site_data["services"]
        load_parties = []
        for party in parties.keys():
            if ServiceThirdPartyEmbeds.ONVIEW not in parties[party]["embed_as"]:
                # This 3rd party is not included when opening the eMail, skip it
                continue
            icons = []
            properties = []
            if parties[party]["receives_address_view"]:
                # Add a leak icon
                icons.append(ICON_LEAK)
            if party.url == site_data["embed"].host:
                # Connections to the first party
                properties.append("first-party")
                icons.append(ICON_FIRSTPARTY)
            load_parties.append(DetailItem(party.name, "#", icons=icons, properties=properties))

        # Include the detected third parties as additional data
        self.check_additional_data = load_parties

        # Set status
        if len(self.check_additional_data) > 0:
            # TODO Potentially set to critical if eMail is leaked?
            self.check_status = STATUS_BAD
            self.check_interpretation = ungettext_lazy("%(count)d newsletter contacts this domain when viewing the mail with remote content enabled.",
                                                       "%(count)d newsletters contact this domain when viewing the mail with remote content enabled.",
                                                       len(self.check_additional_data)) % {'count': len(self.check_additional_data)}
        else:
            self.check_status = STATUS_GOOD
            self.check_interpretation = _("No newsletter contacts this website when being viewed.")
        self.display = True


class EmbedOnClickThirdPartyConnectionCheck(Check):
    """Check if third party services are contacted when clicking a link in the message."""
    check_id = 6
    check_title = _("Contacted on click")
    check_description = _("If this domain is contacted when clicking a link from a newsletter, it is able to track who is clicking which links and when they are doing it. It may also be able to link this information to additional data it may already have about the user.")
    check_condition = _("This check passes if no newsletters (except newsletters sent out by this domain) contact this domain when users click a link.")
    check_error = _("The clicked link from the mail is determined randomly, thus some newsletters may be missed.")
    check_reliability = RELIABILITY_UNRELIABLE

    def __init__(self, site_data):
        if "services" not in site_data:
            logger.error("EmbedOnClickThirdPartyConnectionCheck: Missing services in cache.")
            self.display = False
            return None

        parties = site_data["services"]
        load_parties = []
        for party in parties.keys():
            if ServiceThirdPartyEmbeds.ONCLICK not in parties[party]["embed_as"]:
                # This 3rd party is not included when opening the eMail, skip it
                continue
            if party.name == site_data["service"].name:
                # Connections to the service itself are expected
                continue
            icons = []
            if parties[party]["receives_address_click"]:
                # Add a leak icon
                icons.append(ICON_LEAK)
            load_parties.append(DetailItem(party.name, "#", icons=icons))

        # Include the detected third parties as additional data
        self.check_additional_data = load_parties

        # Set status
        if len(self.check_additional_data) > 0:
            # TODO Potentially set to critical if eMail is leaked?
            self.check_status = STATUS_BAD
            self.check_interpretation = ungettext_lazy("%(count)d newsletter contacts this domain when clicking a link.",
                                                       "%(count)d newsletters contact this domain when clicking a link.",
                                                       len(self.check_additional_data)) % {'count': len(self.check_additional_data)}
        else:
            self.check_status = STATUS_GOOD
            self.check_interpretation = _("No newsletters contact this domain when links are clicked.")
        self.display = True


# class PersonalizedFirstPartyLinkCheck(Check):
#     """Check if the eMail contains personalized links to the domain of the first party."""
#     check_title = _("Personalized links to service")
#     check_description = _("Service providers can track who is opening their links by creating individual links for every recipient. This check attempts to detect the presence of these links by comparing eMails sent to different identities signed up for the same newsletter.")
#     check_condition = _("We allow up to two personalized links per eMail, as we expect unsubscribe links to be personalized.")
#     check_error = _("If an eMail contains more than two management links, this check may falsely claim that links are personalized.")
#     check_reliability = RELIABILITY_RELIABLE


SERVICE_CHECKS = [ServiceThirdPartySpamCheck, ServiceOnViewConnectionCheck, ServiceOnClickThirdPartyConnectionCheck]
EMBED_CHECKS = [EmbedOnViewConnectionCheck, EmbedOnClickThirdPartyConnectionCheck]
