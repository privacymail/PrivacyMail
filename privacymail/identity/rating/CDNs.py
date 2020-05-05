from identity.rating.calculate import scaleToRating, countToRating

from identity.util import filterDict


def CDNs(service):
    return countToRating(
        len(
            filterDict(
                service["third_parties"],
                lambda key, value: "ONVIEW" in value["embed_as"]
                and key.sector != "tracker",
            )
        )
    )


def calculateCDNs(service, weight, maxRating):
    return {
        "weight": weight,
        "rating": scaleToRating(CDNs(service), maxRating),
    }
