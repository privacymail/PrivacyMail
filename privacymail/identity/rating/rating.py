
from identity.rating.emailLeaks import calculateEmailLeaks
from identity.rating.personalizedLinks import calculatePersonalizedLinks
from identity.rating.unpersonalizedLinks import calculateUnpersonalizedLinks
from identity.rating.trackingServices import calculateTrackingServices
from identity.rating.CDNs import calculateCDNs
from identity.rating.ABTesting import calculateABTesting
from identity.rating.calculate import calculateRating

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
        'thirdparties': 5.6,                                    #G103_07
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
        'thirdparties': convertFromSurveyToWeight(1.35),        #G101_13
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


def getRating(service):
    category_rating = {
        'emailLeaks': calculateEmailLeaks(service, weights['emailLeaks'], maxRating['emailLeaks']),
        'personalizedLinks': calculatePersonalizedLinks(service, weights['personalizedLinks'], maxRating['personalizedLinks']),
        'unpersonalizedLinks': calculateUnpersonalizedLinks(service, weights['unpersonalizedLinks'], maxRating['unpersonalizedLinks']),
        'trackingServices': calculateTrackingServices(service, weights['trackingServices'], maxRating['trackingServices']),
        'CDNs': calculateCDNs(service, weights['CDNs'], maxRating['CDNs']), #I just asked about cdns in foreign countires so this value might not be 100% correct
        'ABTesting':calculateABTesting(service, weights['ABTesting'], maxRating['ABTesting']),

    }


    return  calculateRating(category_rating)

