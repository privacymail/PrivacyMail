import { execute } from "./execute";
import { History } from "history";
import { IThirdParty, Reliability } from "./newsletter";

export interface IEmbed {
    embed: IEmbedData;
    services: IThirdParty[];
    country: string;
    sector: string;
    receives_address: boolean;
    sets_cookies: boolean;
    cache_dirty: boolean;
    cache_timestamp: string;
    reliability: {
        mailOpen: Reliability;
        linkClicked: Reliability;
        personalisedLinks: Reliability;
    };
}
export interface IEmbedData {
    host: string;
    name: string;
    resultsdirty: boolean;
    sector: string;
    country_of_origin: string;
}

/**
 * fetched an embed based on id or name
 * @param embed the name or id of the embed
 * @param history the history object of the website so it can redirect to the not found page
 * @param callback function that gets called as soon as the results come in
 */
export const getEmbed = (embed: string = "", history: History, callback: (result: IEmbed) => void): void => {
    let url = "";
    if (embed) {
        if (parseInt(embed)) {
            url = "embed/" + embed;
        } else {
            url = "embed/?url=" + embed;
        }
        execute(url)
            .then((result: any) => {
                //The stuff below is there because thirdparty is in a strange format. When it should return an array then this can be removed
                const oldThirdParties = result.third_parties;
                result.third_parties = [];
                for (const thirdparty in oldThirdParties) {
                    result.third_parties.push(oldThirdParties[thirdparty]);
                }
                callback(result as IEmbed);
            })
            .catch(e => history.push("/embedNotFound/" + embed));
    }
};
/**
 * submits the meta data of an embed
 * @param embed name of the embed
 * @param sector sctor of the embed
 * @param country_of_origin country of the embed
 */
export const postInformationEmbed = (embed: string = "", sector: string, country_of_origin: string): void => {
    let url = "embed/";
    if (embed) {
        const payload = {
            embedID: embed,
            country_of_origin,
            sector
        };
        execute(url, "POST", payload).then((result: any) => {
            window.location.reload();
        });
    }
};
