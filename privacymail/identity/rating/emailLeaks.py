from identity.rating.calculate import scaleToRating, calculateRating
from identity.models import Identity

def calculateSpam(service):
    if Identity.objects.filter(service=service, receives_third_party_spam=True).count() > 0:
        return 1
    else:
        return 0


def calculateEmailLeaksThirdparties(
    embeds,
):  # TODO Sicherstellen, dass das so auch richtig ist
    if embeds.filter(leaks_address=True).exists():
        return 1
    else:
        return 0


def calculateEmailLeaks(service, embeds, weights, rMin, rMax):
    categories = {
        "spam": {
            "rating": scaleToRating(calculateSpam(service), rMax["spam"]),
            "weight": weights["spam"],
        },
        "emailLeaks": {
            "rating": scaleToRating(
                calculateEmailLeaksThirdparties(embeds), rMax["thirdparties"]
            ),
            "weight": weights["thirdparties"],
        },
    }

    return calculateRating(categories)
