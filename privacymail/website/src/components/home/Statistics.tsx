import React, { useState, useEffect } from "react";
import { Trans } from "react-i18next";
import { IStatistics, getStatistics } from "../../repository";

import i18n from "../../i18n/i18n";
const Statistics = () => {
    const [statistics, setStatistics] = useState<IStatistics>();
    useEffect(() => getStatistics(setStatistics), []);

    return (
        <div className="grid statistic">
            <div className="grid-item-4 ">
                <h5>{statistics?.email_count.toLocaleString(i18n.language) ?? "..."}</h5>
                <p className="regular normal">
                    <Trans>home_emailsAnalysied</Trans>
                </p>
            </div>
            <div className="grid-item-4 ">
                <h5>{statistics?.tracker_count.toLocaleString(i18n.language) ?? "..."}</h5>
                <p className="regular normal">
                    <Trans>home_found3rdPraties</Trans>
                </p>
            </div>
            <div className="grid-item-4 ">
                <h5>{statistics?.service_count.toLocaleString(i18n.language) ?? "..."}</h5>
                <p className="regular normal">
                    <Trans>home_registeredNewsletters</Trans>
                </p>
            </div>
        </div>
    );
};
export default Statistics;
