from identity.rating.calculate import (
    scaleToRating,
    calculateRating,
    countToRating,
)
from identity.util import filterDict


def calculatePersonalizedLinksToOwnWebsite(service, rMin, rMax):  # TODO
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
    service, rMin, rMax
):  # TODO should I filter the links to the newsletters own site?
    return countToRating(
        len(
            filterDict(
                service["third_parties"],
                lambda key, value: "ONCLICK" in value["embed_as"]
                and key.name != service["service"].name
                and value["receives_identifier"],
            )
        ),
        rMin,
        rMax,
    )


def calculatePersonalizedLinks(service, weights, rMin, rMax):
    categories = {
        "toOwnWebsite": {
            "rating": scaleToRating(
                calculatePersonalizedLinksToOwnWebsite(
                    service, rMin["toOwnWebsite"], rMax["toOwnWebsite"],
                ),
                rMax["toOwnWebsite"],
            ),
            "weight": weights["toOwnWebsite"],
        },
        "toThirdParties": {
            "rating": scaleToRating(
                calculatePersonalizedLinksThirdParties(
                    service, rMin["toOwnWebsite"], rMax["toOwnWebsite"]
                ),
                rMax["toOwnWebsite"],
            ),
            "weight": weights["toThirdParties"],
        },
    }

    return calculateRating(categories)
