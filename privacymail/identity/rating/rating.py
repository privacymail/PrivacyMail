from identity.rating.emailLeaks import calculateEmailLeaks
from identity.rating.personalizedLinks import calculatePersonalizedLinks
from identity.rating.unpersonalizedLinks import calculateUnpersonalizedLinks
from identity.rating.trackingServices import calculateTrackingServices
from identity.rating.loadedResources import calculateCDNs
from identity.rating.ABTesting import calculateABTesting
from identity.rating.calculate import calculateRating

minRating = 1
maxRating = 6

rMin = {
    "emailLeaks": {
        "spam": 5.85,  # G101_14
        "thirdparties": 5.6,  # G103_07
    },
    "personalizedLinks": {
        "toOwnWebsite": 3.62,  # G103_01
        "toThirdParties": 4.12,  # G103_04
    },
    "unpersonalizedLinks": {
        "toOwnWebsite": 1.1,  # G103_02
        "toThirdParties": 1.1,  # G103_02
        "toTrackers": 2.11,  # G103_02
    },
    "loadedResources": 2.82,  # G101_11
    "trackingServices": {
        "highNumber": 4.34,  # G103_03
        "bigTrackers": 4.72,  # G103_06
        "smallTrackers": 4.34,  # G103_05
    },
    "ABTesting": 3.56,  # G101_01
}
rMax = {
    "emailLeaks": {
        "spam": 5.85,  # G101_14
        "thirdparties": 5.6,  # G103_07
    },
    "personalizedLinks": {
        "toOwnWebsite": 3.62,  # G103_01
        "toThirdParties": 5.11,  # G103_04
    },
    "unpersonalizedLinks": {
        "toOwnWebsite": 1.1,  # G103_02
        "toThirdParties": 1.61,  # G103_02
        "toTrackers": 3.2,  # G103_02
    },
    "loadedResources": 3.32,  # G101_11
    "trackingServices": {
        "highNumber": 5.48,  # G103_03
        "bigTrackers": 5.48,  # G103_06
        "smallTrackers": 4.87,  # G103_05,rMin, rMax
    },
    "ABTesting": 3.56,  # G101_01
}

weights = {
    "emailLeaks": {
        "spam": 57.68,  # G101_14
        "thirdparties": 50.21,  # G103_07
    },
    "personalizedLinks": {
        "toOwnWebsite": 31.56,  # G103_01
        "toThirdParties": 38.59,  # G103_04
    },
    "unpersonalizedLinks": {
        "toOwnWebsite": 3.73,  # G103_02
        "toThirdParties": 9.19,  # G103_02
        "toTrackers": 9.19,  # G103_02
    },
    "loadedResources": 14.12,  # G101_11
    "trackingServices": {
        "highNumber": 26.53,  # G103_03
        "bigTrackers": 38.59,  # G103_06
        "smallTrackers": 20.25,  # G103_05
    },
    "ABTesting": 11.79,  # G101_01
}


def getRating(service):
    category_rating = {
        "emailLeaks": calculateEmailLeaks(
            service, weights["emailLeaks"], rMin["emailLeaks"], rMax["emailLeaks"]
        ),
        "personalizedLinks": calculatePersonalizedLinks(
            service,
            weights["personalizedLinks"],
            rMin["personalizedLinks"],
            rMax["personalizedLinks"],
        ),
        "unpersonalizedLinks": calculateUnpersonalizedLinks(
            service,
            weights["unpersonalizedLinks"],
            rMin["unpersonalizedLinks"],
            rMax["unpersonalizedLinks"],
        ),
        "trackingServices": calculateTrackingServices(
            service,
            weights["trackingServices"],
            rMin["trackingServices"],
            rMax["trackingServices"],
        ),
        "loadedResources": calculateCDNs(
            service,
            weights["loadedResources"],
            rMin["loadedResources"],
            rMax["loadedResources"],
        ),
        "ABTesting": calculateABTesting(
            service, weights["ABTesting"], rMin["ABTesting"], rMax["ABTesting"]
        ),
    }

    return calculateRating(category_rating)
