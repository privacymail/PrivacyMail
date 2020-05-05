from identity.rating.calculate import scaleToRating


def calculateABTesting(service, weight, maxRating):
    if service["suspected_AB_testing"]:
        rating = 1
    else:
        rating = 0

    return {
        "weight": weight,
        "rating": scaleToRating(rating, maxRating),
    }
