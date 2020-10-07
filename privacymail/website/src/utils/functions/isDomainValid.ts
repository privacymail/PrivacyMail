const isValidDomain = require("is-valid-domain");

/**
 * Wraps the isValidDomain function of the corresponing npm module
 * @param domain String of the domain to be checked
 */
export const isDomainVaild = (domain: string): boolean => {
    return isValidDomain(domain, { subdomain: false, wildcard: false });
};
