from identity.rating.calculate import (
    scaleToRating,
    calculateRating,
    countToRating,
)
from identity.util import filterDict
from django.core.cache import cache
from django.db.models import Q
from mailfetcher.models import Thirdparty

from identity.models import ServiceThirdPartyEmbeds, Service

def highNumber(embeds, service, rMin, rMax):
    return countToRating(
        embeds.filter(
            ((Q(embed_type=ServiceThirdPartyEmbeds.ONVIEW) & 
            (Q(thirdparty__sector="tracker") | Q(thirdparty__sector="unkown"))) |
            (Q(embed_type=ServiceThirdPartyEmbeds.ONCLICK) & 
            (Q(thirdparty__sector="tracker") | Q(thirdparty__sector="unkown"))) &
            Q(thirdparty__name = service.name))
        ).count(),
        rMin,
        rMax,
    )

def trackers(embeds,service, rMin, rMax):
    tracker_embeds = embeds.filter(
            ((Q(embed_type=ServiceThirdPartyEmbeds.ONVIEW) & 
            (Q(thirdparty__sector="tracker") | Q(thirdparty__sector="unkown"))) |
            (Q(embed_type=ServiceThirdPartyEmbeds.ONCLICK) & 
            (Q(thirdparty__sector="tracker") | Q(thirdparty__sector="unkown"))) &
            Q(thirdparty__name = service.name))
        ).count(),
    big = 0
    small = 0

    for tracker_embed in tracker_embeds:
        if Service.objects.filter(thirdparties=tracker_embed.thirdparty).count() > 10 :
            big=big+1
        else :
            small=small+1

    return countToRating(
        big * 2 + small,
        rMin,
        rMax,
    )


def calculateTrackingServices(embeds, service, weights, rMin, rMax):
    return {
        "weight": weights["bigTrackers"],
        "rating": scaleToRating(
            trackers(service, embeds, rMin["smallTrackers"], rMax["bigTrackers"]),
            rMax["bigTrackers"],
        ),
    }
