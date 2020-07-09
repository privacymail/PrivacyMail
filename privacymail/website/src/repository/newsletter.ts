import { execute } from "./execute";
import { History } from "history";

export enum Reliability {
    Reliabile = "reliabile",
    Unreliabile = "unreliabile"
}
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
    reliability: {
        mailOpen: Reliability;
        linkClicked: Reliability;
        abTesting: Reliability;
        spam: Reliability;
        personalisedLinks: Reliability;
    };
    rating: IRating;
}
export interface IRating {
    rating: number;
    categories: {
        [category: string]: IRatingCategory;
    };
}
export interface IRatingCategory {
    categories?: IRating;
    rating: number;
    weight?: number;
}
export interface IThirdParty {
    embed_as: string[];
    address_leak_view: boolean;
    address_leak_click: boolean;
    sets_cookie: boolean;
    receives_identifier: boolean;
    name: string;
    host?: string;
    url?: string;
    permitted_senders?: string[];
    hasApprovedIdentity?: boolean;
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
/**
 * fetched an service based on id or name
 * @param service the name or id of the service
 * @param history the history object of the website so it can redirect to the not found page
 * @param callback function that gets called as soon as the results come in
 */
export const getNewsletter = (service: any = "", history: History, callback: (result: INewsletter) => void): void => {
    let url = "";
    if (service) {
        if (!isNaN(service)) {
            url = "service/" + service;
        } else {
            url = "service/?url=" + service;
        }
        execute(url)
            .then((result: any) => {
                //The stuff below is there because thirdparty is in a strange format. When it should return an array then this can be removed
                const oldThirdParties = result.third_parties;
                result.third_parties = [];
                for (const thirdparty in oldThirdParties) {
                    result.third_parties.push(oldThirdParties[thirdparty]);
                }
                callback(result as INewsletter);
            })
            .catch(e => history.push("/serviceNotFound/" + service));
    }
};
/**
 * submits the meta data of an service
 * @param service name of the service
 * @param sector sctor of the service
 * @param country_of_origin country of the service
 */
export const postInformation = (service: string = "", sector: string, country_of_origin: string): void => {
    let url = "service/";
    if (service) {
        const payload = {
            serviceID: service,
            country_of_origin,
            sector
        };

        execute(url, "POST", payload).then((result: any) => {
            window.location.reload();
        });
    }
};
