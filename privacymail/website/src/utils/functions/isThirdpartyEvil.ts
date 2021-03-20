import { IThirdParty } from "../../repository";
/**
 * Checks if a given thirdparty is considered "evil"
 * @param thirdparty The thirdparty that needs to be checked
 */
export const isThirdpartyEvil = (thirdparty?: IThirdParty): boolean => {
    return (
        !!thirdparty &&
        (thirdparty.sector === "tracker" || thirdparty.receives_identifier || !!thirdparty.address_leak_click)
    );
};

/**
 * Checks if a thirdparty is considered "evil" in a given set of thirdparties
 * @param thirdparty The thirdpartys that need to be checked
 */
export const areThirdpartiesEvil = (thirdparties?: IThirdParty[]): boolean => {
    return !!thirdparties && thirdparties.some(thirdparty => isThirdpartyEvil(thirdparty));
};
