import React, { useState, useEffect } from "react";
import { Trans } from "react-i18next";
import { useParams, withRouter, RouteComponentProps } from "react-router-dom";
import { getEmailAnalysis, IEmailAnalysis } from "../../repository";
/**
 * This generates the On Demand Site
 */
const OnDemand = () => {
    const [emailAnalysis, setEmailAnalysis] = useState<IEmailAnalysis>();
    const [rawMail, setRawMail] = useState<string>("");
    return (
        <div>
            <h1>
                <Trans>onDemand_headline</Trans>
            </h1>
            <textarea id="text" value={rawMail} placeholder="Hier Raw-Email eingeben" onChange={e => setRawMail(e.target.value)} />
            <button onClick={e => getEmailAnalysis(rawMail, (analysis: IEmailAnalysis) => {setEmailAnalysis(analysis)})}>Send </button>
            <p>{emailAnalysis?.Message}</p>
        </div>
    );
};

export default OnDemand;
