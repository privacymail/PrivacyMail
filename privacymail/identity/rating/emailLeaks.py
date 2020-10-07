from identity.rating.calculate import scaleToRating, calculateRating


def calculateSpam(service):
    if service["third_party_spam"] > 0:
        return 1
    else:
        return 0


def calculateEmailLeaksThirdparties(
    service,
):  # TODO Sicherstellen, dass das so auch richtig ist
    if service["leaks_address"]:
        return 1
    else:
        return 0


def calculateEmailLeaks(service, weights, rMin, rMax):
    categories = {
        "spam": {
            "rating": scaleToRating(calculateSpam(service), rMax["spam"]),
            "weight": weights["spam"],
        },
        "emailLeaks": {
            "rating": scaleToRating(
                calculateEmailLeaksThirdparties(service), rMax["thirdparties"]
            ),
            "weight": weights["thirdparties"],
        },
    }

    return calculateRating(categories)
