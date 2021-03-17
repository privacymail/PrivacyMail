from datetime import datetime, timedelta

from mailfetcher.models import Mail

def scaleToRating(value, rMax):
    return (value * (rMax- 1)) + 1


def countToRating(count, minRating, maxRating):
    a = (minRating - 1) / (maxRating - 1)
    return -pow(1 - a, count) + 1


def getAccumulateWeights(categories):
    weights = 0
    for key in categories:
        if isinstance(categories[key]["weight"], (int, float, complex)):
            weights += categories[key]["weight"]
    return weights


def getWeightedRating(categories):
    weights = 0
    accumulatedWeightedRating = 0

    for key in categories:
        if isinstance(categories[key]["weight"], (int, float, complex)) and isinstance(
            categories[key]["rating"], (int, float, complex)
        ):
            weights += categories[key]["weight"]
            accumulatedWeightedRating += (
                categories[key]["rating"] * categories[key]["weight"]
            )

    return accumulatedWeightedRating / weights


def flattenCategories(categories, prefix=""):
    flatten = {}
    for category, value in categories.items():

        if "categories" in value:
            flatten = {**flatten, **flattenCategories(value["categories"], category)}
        else:
            key = prefix + category
            flatten[key] = {
                "rating": value["rating"],
                "weight": value["weight"],
            }
    return flatten


def calculateRating(categories):
    flattend = flattenCategories(categories)

    maxRating= 1
    maxCategory = ""

    for (category, value) in flattend.items():
        if maxRating<= value["rating"]:
            maxRating= value["rating"]
            maxCategory = category

    accumulatedWeights = 0
    weightedRating = 0
    for (category, value) in flattend.items():
        if category != maxCategory:
            accumulatedWeights += value["weight"]
            weightedRating += value["rating"] * value["weight"]

    penalty = ((weightedRating / accumulatedWeights) - 1) / 5

    rating = maxRating+ penalty
    if rating > 6:
        rating = 6

    return {"rating": rating, "penalty": penalty, "categories": categories}

def mergeRating(accumulated, new_rating, weight):
    accRating = 0
    accPenalty = 0
    accCategories = {}

    newRating = 0
    newPenalty = 0

    if "rating" in new_rating:
        newRating = new_rating["rating"]
    if "penalty" in new_rating:
        newPenalty = new_rating["penalty"]

    if "rating" in accumulated:
        accRating = accumulated["rating"]
    if "penalty" in accumulated:
        accPenalty = accumulated["penalty"]

    if "categories" in accumulated:
        for key, category in accumulated["categories"].items():
            accCategories[key] = mergeRating( category, new_rating["categories"][key], weight)
    elif "categories" in new_rating:
        for key, category in new_rating["categories"].items():
            accCategories[key] = mergeRating( {}, category, weight)

    return {
        "rating": accRating * (1 - weight) + newRating * weight,
        "penalty": accPenalty * (1 - weight) + newPenalty * weight,
        "categories": accCategories
        }

def calculateAccumulativeRating(ratings):

    identsRating = {}
    identsMailRatingHistory = {}
    worstIdent= None
    worstIdentRating = 0

    for identity in ratings:
        wheigt = 1
        accRating = {}

        identsMailRatingHistory[identity] = []

        for mail, rating in ratings[identity].items():
            accRating = mergeRating(accRating, rating, 1 / wheigt)

            rating["date"] = mail.date_time
            identsMailRatingHistory[identity].append(rating)
            identsRating[identity] = accRating

            if wheigt < 5:
                wheigt = wheigt + 1
            else:
                wheigt = wheigt + 2

        if "rating" in accRating and  accRating["rating"] > worstIdentRating:
            worstIdentRating = identsRating[identity]["rating"]
            worstIdent = identity   

    completeHistory = {}
    i = 0
    for identity, rating in identsMailRatingHistory.items():
        if identity == worstIdent:
            completeHistory["worstIdent"] = rating
        else : 
            completeHistory["identity"+str(i)] = rating
            i = i +1

    if worstIdent is not None:
        return {
            "newsletterRating" : identsRating[worstIdent],
            "history": identsMailRatingHistory[worstIdent],
            "completeHistory" : completeHistory
        }
    else: 
        return {
            "rating" : "NA"
        }