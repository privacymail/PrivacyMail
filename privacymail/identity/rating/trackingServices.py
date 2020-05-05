from identity.rating.calculate import (
    scaleToRating,
    calculateRating,
    countToRating,
)
from identity.util import filterDict


def highNumber(service):
    return countToRating(
        len(
            filterDict(
                service["third_parties"],
                lambda key, value: "ONVIEW" in value["embed_as"]
                and (key.sector == "tracker" or key.sector == "unknown"),
            )
        )
    )


def highNumbersOnLinks(service):
    return countToRating(
        len(
            filterDict(
                service["third_parties"],
                lambda key, value: "ONCLICK" in value["embed_as"]
                and (
                    key.sector == "tracker" or key.sector == "unknown"
                ),  # This unknown might be over sensitv because a lot of thirdparties are not classified yet
            )
        )
    )


def bigTrackers(service):
    return countToRating(
        len(
            filterDict(
                service["third_parties"],
                lambda key, value: (
                    (key.sector == "tracker" or key.sector == "unknown")
                    and len(key.services.all()) > 10  # what defines a big tracker
                    and not print(key)
                    and print(len(key.services.all()))
                ),
            )
        )
    )


def smallTrackers(service):
    return countToRating(
        len(
            filterDict(
                service["third_parties"],
                lambda key, value: (
                    (key.sector == "tracker" or key.sector == "unknown")
                    and len(key.services.all()) <= 10  # what defines a big tracker
                ),
            )
        )
    )


def calculateTrackingServices(service, weights, maxRatings):
    categories = {
        "highNumber": {
            "rating": scaleToRating(highNumber(service), maxRatings["highNumber"]),
            "weight": weights["highNumber"],
        },
        "highNumbersOnLinks": {
            "rating": scaleToRating(
                highNumbersOnLinks(service), maxRatings["highNumbersOnLinks"]
            ),
            "weight": weights["highNumbersOnLinks"],
        },
        "bigTrackers": {
            "rating": scaleToRating(bigTrackers(service), maxRatings["bigTrackers"]),
            "weight": weights["bigTrackers"],
        },
        "smallTrackers": {
            "rating": scaleToRating(
                smallTrackers(service), maxRatings["smallTrackers"]
            ),
            "weight": weights["smallTrackers"],
        },
    }

    return {
        "categories": categories,
        "rating": calculateRating(categories),
    }
