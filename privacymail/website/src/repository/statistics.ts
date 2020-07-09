import { execute } from "./execute";

export interface IGlobalStats {
    global_stats: IStatistics;
}
export interface IStatistics {
    email_count: number;
    service_count: number;
    tracker_count: number;
}
/**
 * fetches the statistics for the PrivacyMail Homepage
 * @param callback function that gets called as soon as the identity comes in
 */
export const getStatistics = (callback: (result: IStatistics) => void): void => {
    execute("statistics").then((result: IGlobalStats) => callback(result.global_stats));
};
