import tldextract
import validators


def validate_domain(domain):
    """Validate a given domain, returning either its canonical form or throw an Exception if it is invalid.

    :param domain: The Domain as a string
    :return: The canonical name of the domain as a string.
    """
    # Remove leading and trailing whitespaces
    domain = domain.strip()
    # Coerce to lower case
    domain = domain.lower()
    # Check if the domain is a valid domain or URL
    if is_valid_domain(domain):
        # Disassemble domain and reassemble in canonical form
        extract = tldextract.extract(domain)
        domain = "{}.{}".format(extract.domain, extract.suffix)
        return domain
    else:
        # String does not encode domain or URL, return None.
        raise AssertionError("Invalid domain provided")


def is_valid_domain(domain):
    """Check if the provided string is a valid domain or url.

    :param domain: Domain as string
    :return: True if the provided string is a valid domain or URL, otherwise false.
    """
    return validators.domain(domain) or validators.url(domain)

def convertForJsonResponse(obj):
    json = {}
    if isinstance(obj, dict):
        i = 0
        hasStringKey = False

        for key in obj:
            if isinstance(key, str):
                hasStringKey = True

        if not hasStringKey:
            json = []

        for key in obj:
            if isinstance(key, str):
                json[key] = executeToJSON(obj[key])
            else:
                if hasStringKey:
                    json[i] = {**executeToJSON(obj[key]) , **executeToJSON(key)}
                else: 
                    json.append({**executeToJSON(obj[key]) , **executeToJSON(key)})
            i=i+1

    elif isinstance(obj, list):
        json=[]
        for i in range(len(obj)):
            json.append(executeToJSON(obj[i]))
    else:
        json = executeToJSON(obj, True)
    
    return json

def executeToJSON(obj, stopFunction=False):
    json = {}
    try:
        json = obj.toJSON()

    except AttributeError:
        json = obj
        if not stopFunction:
            json = convertForJsonResponse(obj)
  
    return json