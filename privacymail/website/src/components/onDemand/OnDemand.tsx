import React, { useState } from "react";
import { Trans } from "react-i18next";
import { getEmailAnalysis, IEmailAnalysis } from "../../repository";
import OnDemandAnalysis from "./OnDemandAnalysis";
import OnDemandInput from "./OnDemandInput";
/**
 * This generates the On Demand Sited
 */
const OnDemand = () => {
    let session;

    try {
        session = JSON.parse(sessionStorage.getItem("emailAnalysis") ?? "");
    } catch (error) {
        session = undefined;
    }
    const [emailAnalysis, setEmailAnalysis] = useState<IEmailAnalysis | undefined>(session);
    const [rawEmail, setRawEmail] = useState<string>("");
    const [viewAnalysis, setViewAnalysis] = useState<boolean>(session ? true : false);
    const runAnalysis = () => {
        setViewAnalysis(true);
        setEmailAnalysis(undefined);
        sessionStorage.removeItem("emailAnalysis");
        getEmailAnalysis(rawEmail, (analysis: IEmailAnalysis | null) => {
            if (analysis) {
                setEmailAnalysis(analysis);
                sessionStorage.setItem("emailAnalysis", JSON.stringify(analysis));
            } else {
                setViewAnalysis(false);
            }
        });
    };

    const returnToInput = () => {
        sessionStorage.removeItem("emailAnalysis");
        setViewAnalysis(false);
    };

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
