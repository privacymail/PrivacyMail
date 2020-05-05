from identity.rating.calculate import (
    scaleToRating,
    calculateRating,
    countToRating,
)
from identity.util import filterDict


def toOwnWebsite(service):
    return len(
        filterDict(
            service["third_parties"],
            lambda key, value: "ONCLICK" in value["embed_as"]
            and key.name == service["service"].name
            and not value["receives_identifier"],
        )
    )


def toThirdParties(
    service,
):  # TODO should I filter the links to the newsletters own site?
    return countToRating(
        len(
            filterDict(
                service["third_parties"],
                lambda key, value: "ONCLICK" in value["embed_as"]
                and key.name != service["service"].name
                and not value["receives_identifier"],
            )
        )
    )


def toForeignCountries(service):
    return countToRating(
        len(
            filterDict(
                service["third_parties"],
                lambda key, value: "ONCLICK" in value["embed_as"]
                and key.country_of_origin != ""
                and service["service"].country_of_origin != ""
                and key.country_of_origin == service["service"].country_of_origin,
            )
        )
    )


def calculateUnpersonalizedLinks(service, weights, maxRatings):
    categories = {
        "toOwnWebsite": {
            "rating": scaleToRating(toOwnWebsite(service), maxRatings["toOwnWebsite"]),
            "weight": weights["toOwnWebsite"],
        },
        "toThirdParties": {
            "rating": scaleToRating(
                toThirdParties(service), maxRatings["toThirdParties"]
            ),
            "weight": weights["toThirdParties"],
        },
        "toForeignCountries": {
            "rating": scaleToRating(
                toForeignCountries(service), maxRatings["toForeignCountries"]
            ),
            "weight": weights["toForeignCountries"],
        },
    }

    return {
        "categories": categories,
        "rating": calculateRating(categories),
    }
