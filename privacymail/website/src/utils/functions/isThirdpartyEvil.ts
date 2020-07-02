import { IThirdParty } from "../../repository";

export const isThirdpartyEvil = (thirdparty?: IThirdParty): boolean => {
    return (
        !!thirdparty &&
        (thirdparty.sector === "tracker" || thirdparty.receives_identifier || thirdparty.address_leak_click)
    );
};
export const areThirdpartiesEvil = (thirdparties?: IThirdParty[]): boolean => {
    return !!thirdparties && thirdparties.some(thirdparty => isThirdpartyEvil(thirdparty));
};
