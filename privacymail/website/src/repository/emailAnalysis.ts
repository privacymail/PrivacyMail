import { execute } from "./execute";
import { History } from "history";

export interface IEmailAnalysis {
    Message: string;
}

/**
 * fetched an service based on id or name
 * @param service the name or id of the service
 * @param history the history object of the website so it can redirect to the not found page
 * @param callback function that gets called as soon as the results come in
 */
export const getEmailAnalysis = (rawData: string,  callback: (result: IEmailAnalysis) => void): void => {
    execute("analysis", "POST", { rawData})
    .then((result: any) => {
                callback(result as IEmailAnalysis);
    })
};
