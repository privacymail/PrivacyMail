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


def bigTrackers(service):

    return len(
        filterDict(
            service["third_parties"],
            lambda key, value: (
                (
                    (
                        "ONVIEW" in value["embed_as"]
                        and (key.sector == "tracker" or key.sector == "unknown")
                    )
                    or ("ONCLICK" in value["embed_as"] and (key.sector == "tracker"))
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
    )


def smallTrackers(service):
    return len(
        filterDict(
            service["third_parties"],
            lambda key, value: (
                (
                    (
                        "ONVIEW" in value["embed_as"]
                        and (key.sector == "tracker" or key.sector == "unknown")
                    )
                    or ("ONCLICK" in value["embed_as"] and (key.sector == "tracker"))
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
    )


def trackers(service, rMin, rMax):
    return countToRating(bigTrackers(service) * 2 + smallTrackers(service), rMin, rMax,)


def calculateTrackingServices(service, weights, rMin, rMax):
    return {
        "weight": weights["bigTrackers"],
        "rating": scaleToRating(
            trackers(service, rMin["smallTrackers"], rMax["bigTrackers"]),
            rMax["bigTrackers"],
        ),
    }
