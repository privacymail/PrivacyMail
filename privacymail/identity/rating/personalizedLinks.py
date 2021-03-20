from identity.rating.calculate import (
    scaleToRating,
    calculateRating,
    countToRating,
)
from django.db.models import Q
from identity.util import filterDict
from identity.models import ServiceThirdPartyEmbeds


def calculatePersonalizedLinksToOwnWebsite(embeds,service, rMin, rMax):
    if embeds.filter(
        (Q(embed_type=ServiceThirdPartyEmbeds.ONCLICK) | Q(embed_type=ServiceThirdPartyEmbeds.STATIC)) &
        Q(thirdparty__name=service.name) & 
        Q(receives_identifier=True)
        ).count() >= 1:
        return 1
    else:
        return 0


def calculatePersonalizedLinksThirdParties(
    embeds,service, rMin, rMax
):  # TODO should I filter the links to the newsletters own site?
    return countToRating(
        embeds.filter(
            (Q(embed_type=ServiceThirdPartyEmbeds.ONCLICK) | Q(embed_type=ServiceThirdPartyEmbeds.STATIC)) &
            ~Q(thirdparty__name=service.name) & 
            Q(receives_identifier=True)
        ).count(),
        rMin,
        rMax,
    )


def calculatePersonalizedLinks(embeds,service, weights, rMin, rMax):
    categories = {
        "toOwnWebsite": {
            "rating": scaleToRating(
                calculatePersonalizedLinksToOwnWebsite(
                    embeds,service, rMin["toOwnWebsite"], rMax["toOwnWebsite"],
                ),
                rMax["toOwnWebsite"],
            ),
            "weight": weights["toOwnWebsite"],
        },
        "toThirdParties": {
            "rating": scaleToRating(
                calculatePersonalizedLinksThirdParties(
                    embeds,service, rMin["toThirdParties"], rMax["toThirdParties"]
                ),
                rMax["toThirdParties"],
            ),
            "weight": weights["toThirdParties"],
        },
    }

    return calculateRating(categories)
