import { execute } from "./execute";

export interface IEmailAnalysis {
    eresources_on_view: number;
    directly_embedded_eresources: number;
    directly_embedded_third_party: number;
    third_parties: string[];
    additionaly_loaded_parties: string[];
    num_of_leaks_to_third_parties: number;
    num_of_leaks_through_forwards: number;
    leak_eresource_set_count: number;
    additionaly_loaded__third_party_count: number;
    leaking_methods: [];
    cookies: boolean;
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
        .catch(e => callback(null));
};
