
minRating = 1
maxRating = 6

# These are calutlated by 0.5^x. While x is the value found in the survey/
def convertFromSurveyToWeight(x):
    return pow(0.5, x)

# There is not enough data for every category. So for needs to be a conversion for every missing category
def convertFromSurveyToRating(x):
    return maxRating - (x-minRating)

maxRating = {
    'emailLeaks': {
        'spam': convertFromSurveyToRating(1.15),                #G101_14
        'thridparties': 5.6,                                    #G103_07
    },
    'personalizedLinks': {
        'toOwnWebsite' : 3.62,                                  #G103_01
        'toThirdParties' : 5.11                                 #G103_04
    },
    'unpersonalizedLinks': {
        'toOwnWebsite': 1.61,                                   #G103_02
        'toThirdParties': 1.61,                                 #G103_02
        'toForeignCountries': 1.61,                             #G103_02
    },
    'trackingServices': {
        'highNumber': 5.48,                                     #G103_03
        'highNumbersOnLinks': convertFromSurveyToRating(2.27),  #G101_03
        'bigTrackers': 4.72,                                    #G103_06
        'smallTrackers': 4.87                                   #G103_05
    },
    'CDNs': convertFromSurveyToRating(3.18),                    #G101_11
    'ABTesting':convertFromSurveyToRating(3.44)                 #G101_01
}

weights = {
    'emailLeaks': {
        'spam': convertFromSurveyToWeight(1.15),                #G101_14
        'thridparties': convertFromSurveyToWeight(1.35),        #G101_13
    },
    'personalizedLinks': {
        'toOwnWebsite' : convertFromSurveyToWeight(2.02),       #G101_07
        'toThirdParties' : convertFromSurveyToWeight(1.73)      #G101_08
    },
    'unpersonalizedLinks': {
        'toOwnWebsite': convertFromSurveyToWeight(5.1),         #G101_09
        'toThirdParties': convertFromSurveyToWeight(3.8),       #G101_10
        'toForeignCountries': convertFromSurveyToWeight(4.21)   #G101_12
    },
    'trackingServices': {
        'highNumber': convertFromSurveyToWeight(1.93),          #G101_02
        'highNumbersOnLinks': convertFromSurveyToWeight(2.27),  #G101_03
        'bigTrackers': convertFromSurveyToWeight(1.73),         #G101_04
        'smallTrackers' :convertFromSurveyToWeight(2.66)        #G101_05
    },
    'CDNs': convertFromSurveyToWeight(3.18),                    #G101_11
    'ABTesting':convertFromSurveyToWeight(3.44)                 #G101_01
}


def calculateRating(service):
    category_rating = {
        'emailLeaks': calculateEmailLeaks(service, weights.emailLeaks, maxRating.emailLeaks),
        'personalizedLinks': calculatePersonalizedLinks(service, weights.personalizedLinks, maxRating.personalizedLinks),
        'unpersonalizedLinks': calculateUnpersonalizedLinks(service, weights.unpersonalizedLinks, maxRating.unpersonalizedLinks),
        'trackingServices': calculateTrackingServices(service, weights.trackingServices, maxRating.trackingServices),
        'CDNs': calculateCDNs(service, weights.CDNs, maxRating.CDNs),
        'ABTesting':calculateABTesting(service, weights.ABTesting, maxRating.ABTesting)

    }


    return category_rating

def scaleToRating(value, scale):
    return (value * (scale-1)) + 1

def countToRating(count, slope=0.5):
    return pow(-slope, count) + 1

def getAccumulateWeights(categories):
    weights = 0
    for key in categories:
        if isinstance(categories[key].weight, (int, float, complex)):
            weights+=categories[key].weight
    return weights

def getWeightedRating(categories):
    weights = 0
    accumulatedWeightedRating = 0

    for key in categories:
        if (isinstance(categories[key].weight, (int, float, complex)) and isinstance(categories[key].rating, (int, float, complex))):
            weights+=categories[key].weight
            accumulatedWeightedRating+=categories[key].rating

    return accumulatedWeightedRating / weights




def calculateSpam(service):
    if(service.third_party_spam > 0):
        return 1
    else: 
        return 0

def calculateEmailLeaksThirdparties(service):           #TODO Sicherstellen, dass das so auch richtig ist
    if(service.leaks_address):
        return 1
    else: 
        return 0

def calculateEmailLeaks(service, weights, maxRatings):
    categories = {
        'spam' : {
            'rating': scaleToRating(calculateSpam(service), maxRatings.spam),
            'weight': weights.spam
        },
        'emailLeaks' : {
            'rating': scaleToRating(calculateEmailLeaksThirdparties(service), maxRatings.thirdparties),
            'weight': weights.thirdparties
        },
    }

    return {
        'categories': categories,
        'weight': getAccumulateWeights(categories),
        'rating': getWeightedRating(categories),
    }


def calculatePersonalizedLinksToOwnWebsite(service):    #TODO
    return countToRating(len(list(filter(lambda x: x < 0, number_list)))) 

def calculatePersonalizedLinksThirdParties(service):    #TODO
    return countToRating(len(service.third_parties))

def calculatePersonalizedLinks(service, weights, maxRatings):
    categories = {
        'toOwnWebsite' : {
            'rating': scaleToRating(calculatePersonalizedLinksToOwnWebsite(service), maxRatings.toOwnWebsite),
            'weight': weights.toOwnWebsite
        },
        'toThirdParties' : {
            'rating': scaleToRating(calculatePersonalizedLinksThirdParties(service), maxRatings.toThirdParties),
            'weight': weights.toThirdParties
        },
    }

    return {
        'categories': categories,
        'weight': getAccumulateWeights(categories),
        'rating': getWeightedRating(categories),
    }

def calculateUnpersonalizedLinks(service, weights, maxRatings):
    categories = {
        'toOwnWebsite' : {
            'rating': scaleToRating(calculateSpam(service), maxRatings.toOwnWebsite),
            'weight': weights.toOwnWebsite
        },
        'toThirdParties' : {
            'rating': scaleToRating(calculateEmailLeaksThirdparties(service), maxRatings.toThirdParties),
            'weight': weights.toThirdParties
        },
        'toForeignCountries' : {
            'rating': scaleToRating(calculateEmailLeaksThirdparties(service), maxRatings.toForeignCountries),
            'weight': weights.toForeignCountries
        },
    }

    return {
        'categories': categories,
        'weight': getAccumulateWeights(categories),
        'rating': getWeightedRating(categories),
    }

def calculateTrackingServices(service, weights, maxRatings):
    categories = {
        'highNumber' : {
            'rating': scaleToRating(calculateSpam(service), maxRatings.highNumber),
            'weight': weights.highNumber
        },
        'highNumbersOnLinks' : {
            'rating': scaleToRating(calculateEmailLeaksThirdparties(service), maxRatings.highNumbersOnLinks),
            'weight': weights.highNumbersOnLinks
        },
        'bigTrackers' : {
            'rating': scaleToRating(calculateSpam(service), maxRatings.bigTrackers),
            'weight': weights.bigTrackers
        },
        'smallTrackers' : {
            'rating': scaleToRating(calculateEmailLeaksThirdparties(service), maxRatings.smallTrackers),
            'weight': weights.smallTrackers
        },
    }

    return {
        'categories': categories,
        'weight': getAccumulateWeights(categories),
        'rating': getWeightedRating(categories),
    }

def calculateCDNs(service, weight, maxRating):
    return {
        'weight': weight,
        'rating': scaleToRating(calculateEmailLeaksThirdparties(service), maxRating),
    }

def calculateABTesting(service, weight, maxRating):
    if(service.suspected_AB_testing):
        rating = 1
    else: 
        rating = 0

    return {
        'weight': weight,
        'rating': scaleToRating(rating, maxRating),
    }

