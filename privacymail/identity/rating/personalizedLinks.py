from identity.rating.calculate import (
    scaleToRating,
    calculateRating,
    countToRating,
)
from identity.util import filterDict


def calculatePersonalizedLinksToOwnWebsite(service):  # TODO
    if (
        len(
            filterDict(
                service["third_parties"],
                lambda key, value: "ONCLICK" in value["embed_as"]
                and key.name == service["service"].name
                and value["receives_identifier"],
            )
        )
        >= 1
    ):
        return 1
    else:
        return 0


def calculatePersonalizedLinksThirdParties(
    service,
):  # TODO should I filter the links to the newsletters own site?
    return countToRating(
        len(
            filterDict(
                service["third_parties"],
                lambda key, value: "ONCLICK" in value["embed_as"]
                and key.name != service["service"].name
                and value["receives_identifier"],
            )
        )
    )


def calculatePersonalizedLinks(service, weights, maxRatings):
    categories = {
        "toOwnWebsite": {
            "rating": scaleToRating(
                calculatePersonalizedLinksToOwnWebsite(service),
                maxRatings["toOwnWebsite"],
            ),
            "weight": weights["toOwnWebsite"],
        },
        "toThirdParties": {
            "rating": scaleToRating(
                calculatePersonalizedLinksThirdParties(service),
                maxRatings["toThirdParties"],
            ),
            "weight": weights["toThirdParties"],
        },
    }

    return calculateRating(categories)
