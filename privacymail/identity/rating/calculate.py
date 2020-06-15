def scaleToRating(value, rMax):
    return (value * (rMax - 1)) + 1


def countToRating(count, minRating, maxRating):
    minRating = (minRating-1)/(maxRating-1)
    return -pow(minRating, count) + 1


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
    for (category, value) in categories.items():

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

    max = 1
    maxCategory = ""

    for (category, value) in flattend.items():
        if max <= value["rating"]:
            max = value["rating"]
            maxCategory = category

    accumulatedWeights = 0
    weightedRating = 0
    for (category, value) in flattend.items():
        if category != maxCategory:
            accumulatedWeights += value["weight"]
            weightedRating += value["rating"] * value["weight"]

    penalty = ((weightedRating / accumulatedWeights) - 1) / 5

    rating = max + penalty
    if rating > 6:
        rating = 6

    return {"rating": rating, "penalty": penalty, "categories": categories}
