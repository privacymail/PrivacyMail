import React, { useState, useEffect } from "react";
import { Trans } from "react-i18next";
import { getEmailAnalysis, IEmailAnalysis } from "../../repository";
import OnDemandAnalysis from "./OnDemandAnalysis";
import OnDemandInput from "./OnDemandInput";
/**
 * This generates the On Demand Sited
 */
const OnDemand = () => {
    const [emailAnalysis, setEmailAnalysis] = useState<any>(sessionStorage.getItem("emailAnalysis"));
    const [rawEmail, setRawEmail] = useState<string>("");
    const [viewAnalysis, setViewAnalysis] = useState<boolean>(false);
    const runAnalysis = () => {
        setViewAnalysis(true);
        setEmailAnalysis(null);
        getEmailAnalysis(rawEmail, (analysis: IEmailAnalysis | null) => {
            analysis ? setEmailAnalysis(analysis) : setViewAnalysis(false);
        });
    };

    const returnToInput = () => {
        setViewAnalysis(false);
    };

    useEffect(() => {
        localStorage.setItem("emailAnalysis", emailAnalysis);
    }, [emailAnalysis]);

    return (
        <div>
            <h1>
                <Trans>onDemand_headline</Trans>
            </h1>

            {viewAnalysis ? (
                <OnDemandAnalysis emailAnalysis={emailAnalysis} returnToInput={returnToInput} />
            ) : (
                <OnDemandInput rawEmail={rawEmail} setRawEmail={setRawEmail} runAnalysis={runAnalysis} />
            )}
        </div>
    );
};

export default OnDemand;
