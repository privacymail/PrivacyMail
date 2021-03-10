from identity.rating.calculate import scaleToRating

from identity.models import Identity
from mailfetcher.models import Mail

def calculateABTesting(service, weight,rMin, rMax):
    idents = Identity.objects.filter(service=service)

    if Mail.objects.filter(
        identity__in=idents, 
        identity__approved=True,
        possible_AB_testing=True
    ).exists():
        rating = 1
    else:
        rating = 0

    return {
        "weight": weight,
        "rating": scaleToRating(rating, rMax),
    }
