const isValidDomain = require("is-valid-domain");
export const isDomainVaild = (domain: string): boolean => {
    return isValidDomain(domain, { subdomain: false, wildcard: false });
};
