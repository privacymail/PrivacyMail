import React, { useState, useEffect } from "react";
import { Trans } from "react-i18next";
import { IStatistics, getStatistics } from "../../repository";

const Statistics = () => {
    const [statistics, setStatistics] = useState<IStatistics>();
    useEffect(() => getStatistics(setStatistics), []);

    return (
        <div className="grid statistic">
            <div className="grid-item-4 ">
                <p className="medium biggest">{statistics?.email_count}</p>
                <p className="regular normal">
                    <Trans>home_emailsAnalysied</Trans>
                </p>
            </div>
            <div className="grid-item-4 ">
                <p className="medium biggest">{statistics?.service_count}</p>
                <p className="regular normal">
                    <Trans>home_found3rdPraties</Trans>
                </p>
            </div>
            <div className="grid-item-4 ">
                <p className="medium biggest">{statistics?.tracker_count}</p>
                <p className="regular normal">
                    <Trans>home_registeredNewsletters</Trans>
                </p>
            </div>
        </div>
    );
};
export default Statistics;
