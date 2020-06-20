from identity.rating.calculate import (
    scaleToRating,
    calculateRating,
    countToRating,
)
from identity.util import filterDict
from django.core.cache import cache

from mailfetcher.models import Thirdparty


def highNumber(service, rMin, rMax):
    return countToRating(
        len(
            filterDict(
                service["third_parties"],
                lambda key, value: (
                    (
                        "ONVIEW" in value["embed_as"]
                        and (key.sector == "tracker" or key.sector == "unknown")
                    )
                    or ("ONCLICK" in value["embed_as"] and (key.sector == "tracker"))
                )
                and key.name != service["service"].name,
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
                    (
                        (
                            "ONVIEW" in value["embed_as"]
                            and (key.sector == "tracker" or key.sector == "unknown")
                        )
                        or (
                            "ONCLICK" in value["embed_as"] and (key.sector == "tracker")
                        )
                    )
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
                    (
                        (
                            "ONVIEW" in value["embed_as"]
                            and (key.sector == "tracker" or key.sector == "unknown")
                        )
                        or (
                            "ONCLICK" in value["embed_as"] and (key.sector == "tracker")
                        )
                    )
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
