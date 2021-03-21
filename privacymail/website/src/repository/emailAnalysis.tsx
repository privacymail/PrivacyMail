import React from "react";
import { Trans } from "react-i18next";
import { addTooltipByCord } from "../utils/Tooltip";
import { execute } from "./execute";
import { IThirdParty } from "./newsletter";

export interface IEmailAnalysis {
    homeUrl: string;
    third_parties: IThirdParty[];
    cookies: boolean;
    mailLeakage: boolean;
    eresources: any;
}

/**
 * fetched an service based on id or name
 * @param service the name or id of the service
 * @param history the history object of the website so it can redirect to the not found page
 * @param callback function that gets called as soon as the results come in
 */
export const getEmailAnalysis = (rawData: string, callback: (result: IEmailAnalysis | null) => void): void => {
    execute("analysis", "POST", { rawData })
        .then((result: any) => {
            callback(result as IEmailAnalysis);
        })
        .catch(e => {
            callback(null);
            addTooltipByCord(<Trans>onDemand_error_analysis</Trans>, 0, 0, {
                timeout: 3000,
                className: "tooltip error"
            });
        });
};
