import { execute } from "./execute"

export interface GlobalStats {
    global_stats: Statistics
}
export interface Statistics {
    email_count: number,
    service_count: number,
    tracker_count: number

}
export const getStatistics = (callback: (result: Statistics) => void): void => {
    execute("statistics").then((result: GlobalStats) => callback(result.global_stats));
}