from identity.rating.calculate import (
    scaleToRating,
    calculateRating,
    countToRating,
)
from identity.util import filterDict

from identity.models import ServiceThirdPartyEmbeds
from django.db.models import Q
def toOwnWebsite(embeds,service, rMin, rMax):
    if (embeds.filter(
            (Q(embed_type=ServiceThirdPartyEmbeds.ONCLICK) | Q(embed_type=ServiceThirdPartyEmbeds.STATIC)) &
            Q(thirdparty__name=service.name) & 
            ~Q(receives_identifier=True)
        ).count() >= 1
    ):
        return 1
    else:
        return 0


def toThirdParties(
    embeds, service, rMin, rMax
):  # TODO should I filter the links to the newsletters own site?
    diffrentCountries =  embeds.filter(
            (Q(embed_type=ServiceThirdPartyEmbeds.ONCLICK) | Q(embed_type=ServiceThirdPartyEmbeds.STATIC))
        ).exclude(
            receives_identifier=True, 
            thirdparty__name=service.name,
            thirdparty__country_of_origin= service.country_of_origin
        ).count()
    sameCountry = embeds.filter(
            (Q(embed_type=ServiceThirdPartyEmbeds.ONCLICK) | Q(embed_type=ServiceThirdPartyEmbeds.STATIC)) &
            Q(thirdparty__country_of_origin= service.country_of_origin)
        ).exclude(
            receives_identifier=True, 
            thirdparty__name=service.name
        ).count()
    
    return countToRating(diffrentCountries * 1.5 + sameCountry, rMin, rMax,)


def toTrackers(embeds, service, rMin, rMax):
    return countToRating(
        embeds.filter(
            (Q(embed_type=ServiceThirdPartyEmbeds.ONCLICK) | Q(embed_type=ServiceThirdPartyEmbeds.STATIC))&
            Q(thirdparty__sector = "tracker")
        ).exclude(
            thirdparty__name=service.name
        ).count(),
        rMin,
        rMax,
    )


def calculateUnpersonalizedLinks(embeds, service, weights, rMin, rMax):
    categories = {
        "toOwnWebsite": {
            "rating": scaleToRating(
                toOwnWebsite(embeds, service, rMin["toOwnWebsite"], rMax["toOwnWebsite"]),
                rMax["toOwnWebsite"],
            ),
            "weight": weights["toOwnWebsite"],
        },
        "toThirdParties": {
            "rating": scaleToRating(
                toThirdParties(embeds, service, rMin["toThirdParties"], rMax["toThirdParties"]),
                rMax["toThirdParties"],
            ),
            "weight": weights["toThirdParties"],
        },
        "toTrackers": {
            "rating": scaleToRating(
                toTrackers(embeds, service, rMin["toTrackers"], rMax["toTrackers"]),
                rMax["toTrackers"],
            ),
            "weight": weights["toTrackers"],
        },
    }

    return calculateRating(categories)
