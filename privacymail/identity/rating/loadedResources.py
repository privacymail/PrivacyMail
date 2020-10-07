from identity.rating.calculate import scaleToRating, countToRating

from identity.util import filterDict


def CDNs(service, rMin, rMax):
    return countToRating(
        len(
            filterDict(
                service["third_parties"],
                lambda key, value: "ONVIEW" in value["embed_as"]
                and (
                    (key.sector != "tracker" and key.sector != "unknown")
                    or key.name == service["service"].name
                ),
            )
        ),
        rMin,
        rMax,
    )


def calculateCDNs(service, weight, rMin, rMax):
    return {
        "weight": weight,
        "rating": scaleToRating(CDNs(service, rMin, rMax), rMax),
    }
