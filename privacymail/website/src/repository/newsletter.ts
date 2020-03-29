import { execute } from "./execute";

export interface INewsletter {
    count_mails: number;
    count_mult_ident_mails: number;
    leak_algorithms: string[];
    cookies_set_avg: number;
    third_parties: IThirdParty[];
    percent_links_personalised: number;
    avg_personalised_anchor_links: number;
    avg_personalised_image_links: number;
    num_embedded_links: number;
    suspected_AB_testing: boolean;
    third_party_spam: number;
    cache_dirty: boolean;
    cache_timestamp: string;
    service: IService;
    sets_cookies: boolean;
    num_different_thirdparties: number;
    num_different_idents: number;
    leaks_address: number;
    checks: any[];
}
export interface IThirdParty {
    embed_as: string[];
    address_leak_view: boolean;
    address_leak_click: boolean;
    sets_cookie: boolean;
    receives_identifier: boolean;
    name: string;
    host: string;
    resultsdirty: boolean;
    sector: string;
    service: any;
}
export interface IService {
    url: string;
    name: string;
    permitted_senders: string[];
    resultsdirty: boolean;
    hasApprovedIdentity: boolean;
    sector: string;
    country_of_origin: string;
}
export const getNewsletter = (service: string = "", callback: (result: INewsletter) => void): void => {
    if (service) {
        if (parseInt(service)) {
            service = "service/" + service;
        } else {
            service = "service/?url=" + service;
        }
        execute(service).then((result: any) => {
            //The stuff below is there because thirdparty is in a strange format. When it should return an array then this can be removed
            const oldThirdParties = result.third_parties;
            result.third_parties = [];
            for (const thirdparty in oldThirdParties) {
                result.third_parties.push(oldThirdParties[thirdparty]);
            }
            callback(result as INewsletter);
        });
    }
};
