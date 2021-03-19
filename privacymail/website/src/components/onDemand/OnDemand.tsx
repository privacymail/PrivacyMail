import React, { useState } from "react";
import { Trans } from "react-i18next";
import { getEmailAnalysis, IEmailAnalysis } from "../../repository";
import OnDemandAnalysis from "./OnDemandAnalysis";
import OnDemandInput from "./OnDemandInput";
/**
 * This generates the On Demand Sited
 */
const OnDemand = () => {
    const [emailAnalysis, setEmailAnalysis] = useState<any>();
    const [rawEmail, setRawEmail] = useState<string>("");
    const [viewAnalysis, setViewAnalysis] = useState<boolean>(false);
    const runAnalysis = () => {
        setViewAnalysis(true);
        setEmailAnalysis(null);
        getEmailAnalysis(rawEmail, (analysis: IEmailAnalysis | null) => {
            setEmailAnalysis(analysis);
        });
    };
    const returnToInput = () => {
        setViewAnalysis(false);
    };
    return (
        <div>
            <div className="newsletter">
                <div className="privacyRating">
                    <h1>
                        <Trans>onDemand_headline</Trans>
                    </h1>
                </div>
            </div>

            {viewAnalysis ? (
                <OnDemandAnalysis emailAnalysis={emailAnalysis} returnToInput={returnToInput} />
            ) : (
                <OnDemandInput rawEmail={rawEmail} setRawEmail={setRawEmail} runAnalysis={runAnalysis} />
            )}
        </div>
    );
};

export default OnDemand;
