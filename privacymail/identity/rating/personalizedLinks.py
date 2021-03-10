from identity.rating.calculate import (
    scaleToRating,
    calculateRating,
    countToRating,
)
from identity.util import filterDict
from identity.models import ServiceThirdPartyEmbeds


def calculatePersonalizedLinksToOwnWebsite(embeds,service, rMin, rMax):
    if (embeds.filter(
            embed_type=ServiceThirdPartyEmbeds.ONCLICK, 
            thirdparty__name=service.name, 
            receives_identifier=True
        ).count() >= 1):
        return 1
    else:
        return 0


def calculatePersonalizedLinksThirdParties(
    embeds,service, rMin, rMax
):  # TODO should I filter the links to the newsletters own site?
    return countToRating(
        embeds.filter(
            embed_type=ServiceThirdPartyEmbeds.ONCLICK, 
            receives_identifier=True
        ).exclude(
            thirdparty__name=service.name
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
