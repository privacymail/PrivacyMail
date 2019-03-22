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
