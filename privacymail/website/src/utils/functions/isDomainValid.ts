const isValidDomain = require("is-valid-domain");
export const isDomainVaild = (domain: string): boolean => {
    console.log(domain, isValidDomain(domain, { subdomain: false, wildcard: false }));

    return isValidDomain(domain, { subdomain: false, wildcard: false });
};
