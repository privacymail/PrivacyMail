from identity.rating.calculate import (
    scaleToRating,
    calculateRating,
    countToRating,
)
from identity.util import filterDict


def toOwnWebsite(service, rMin, rMax):
    return len(
        filterDict(
            service["third_parties"],
            lambda key, value: "ONCLICK" in value["embed_as"]
            and key.name == service["service"].name
            and not value["receives_identifier"],
        )
    )


def toThirdParties(
    service, rMin, rMax
):  # TODO should I filter the links to the newsletters own site?

    diffrentCountries = len(
        filterDict(
            service["third_parties"],
            lambda key, value: "ONCLICK" in value["embed_as"]
            and key.name != service["service"].name
            and not value["receives_identifier"],
            and key.country_of_origin != service["service"].country_of_origin,
        )
    )
    sameCountry = len(
        filterDict(
            service["third_parties"],
            lambda key, value: "ONCLICK" in value["embed_as"]
            and key.name != service["service"].name
            and not value["receives_identifier"],
            and key.country_of_origin == service["service"].country_of_origin,
        )
    )
    return countToRating(diffrentCountries * 1.5 + sameCountry, rMin, rMax,)


def toTrackers(service, rMin, rMax):
    return countToRating(
        len(
            filterDict(
                service["third_parties"],
                lambda key, value: "ONCLICK" in value["embed_as"]
                and key.name != service["service"].name
                and (
                    key.sector == "tracker"
                ),  # This unknown might be over sensitv because a lot of thirdparties are not classified yet
            )
        ),
        rMin,
        rMax,
    )


def calculateUnpersonalizedLinks(service, weights, rMin, rMax):
    categories = {
        "toOwnWebsite": {
            "rating": scaleToRating(
                toOwnWebsite(service, rMin["toOwnWebsite"], rMax["toOwnWebsite"]),
                rMax["toOwnWebsite"],
            ),
            "weight": weights["toOwnWebsite"],
        },
        "toThirdParties": {
            "rating": scaleToRating(
                toThirdParties(service, rMin["toThirdParties"], rMax["toThirdParties"]),
                rMax["toThirdParties"],
            ),
            "weight": weights["toThirdParties"],
        },
        "toTrackers": {
            "rating": scaleToRating(
                toTrackers(service, rMin["toTrackers"], rMax["toTrackers"]),
                rMax["toTrackers"],
            ),
            "weight": weights["toTrackers"],
        },
    }

    return calculateRating(categories)
