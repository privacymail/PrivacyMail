from identity.rating.calculate import (
    scaleToRating,
    calculateRating,
    countToRating,
)
from identity.util import filterDict
from django.core.cache import cache

from mailfetcher.models import Thirdparty



def highNumbersOnLinks(service, rMin, rMax):
    return countToRating(
        len(
            filterDict(
                service["third_parties"],
                lambda key, value: "ONCLICK" in value["embed_as"]
                and key.name != service["service"].name
                and (
                    key.sector == "tracker" or key.sector == "unknown"
                ),  # This unknown might be over sensitv because a lot of thirdparties are not classified yet
            )
        ),
        rMin,
        rMax,
    )


def bigTrackers(service, rMin, rMax):

    return countToRating(
        len(
            filterDict(
                service["third_parties"],
                lambda key, value: (
                    (key.sector == "tracker" or key.sector == "unknown")
                    and key.name != service["service"].name
                    and len(
                        cache.get(
                            Thirdparty.objects.get(
                                host=key.name
                            ).derive_thirdparty_cache_path()
                        )["services"]
                    )
                    > 10  # what defines a big tracker
                ),
            )
        ),
        rMin,
        rMax,
    )


def smallTrackers(service, rMin, rMax):
    return countToRating(
        len(
            filterDict(
                service["third_parties"],
                lambda key, value: (
                    (key.sector == "tracker" or key.sector == "unknown")
                    and key.name != service["service"].name
                    and len(
                        cache.get(
                            Thirdparty.objects.get(
                                host=key.name
                            ).derive_thirdparty_cache_path()
                        )["services"]
                    )
                    <= 10  # what defines a big tracker
                ),
            )
        ),
        rMin,
        rMax,
    )


def calculateTrackingServices(service, weights, rMin, rMax):
    categories = {
        "highNumber": {
            "rating": scaleToRating(
                highNumber(service, rMin["highNumber"], rMax["highNumber"]),
                rMax["highNumber"],
            ),
            "weight": weights["highNumber"],
        },
        "bigTrackers": {
            "rating": scaleToRating(
                bigTrackers(service, rMin["bigTrackers"], rMax["bigTrackers"]),
                rMax["bigTrackers"],
            ),
            "weight": weights["bigTrackers"],
        },
        "smallTrackers": {
            "rating": scaleToRating(
                smallTrackers(service, rMin["smallTrackers"], rMax["smallTrackers"]),
                rMax["smallTrackers"],
            ),
            "weight": weights["smallTrackers"],
        },
    }

    return calculateRating(categories)
