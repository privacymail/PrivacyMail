from identity.rating.calculate import scaleToRating, countToRating

from identity.util import filterDict

from identity.models import ServiceThirdPartyEmbeds
from django.db.models import Q

def CDNs(embeds, service, rMin, rMax):
    return countToRating(
        embeds.filter(
            Q(embed_type=ServiceThirdPartyEmbeds.ONVIEW) & 
            ((~Q(thirdparty__sector="tracker") & ~Q(thirdparty__sector="unkown")) | Q(thirdparty__name = service.name))
        ).count(),
        rMin,
        rMax,
    )


def calculateCDNs(embeds, service, weight, rMin, rMax):
    return {
        "weight": weight,
        "rating": scaleToRating(CDNs(embeds,service, rMin, rMax), rMax),
    }
