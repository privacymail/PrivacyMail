import React from "react";
import { Trans } from "react-i18next";
import { INewsletter } from "../../../repository";
import OnOpenThirdparties from "./OnOpenThirdparties";
import OnClickThirdparties from "./OnClickThirdparties";
import ABTesting from "./ABTesting";

interface AnalysisProps {
    newsletter?: INewsletter;
}

const Analysis = (props: AnalysisProps) => {
    const onOpenThirdparties = props.newsletter?.third_parties.filter(thirdpartie =>
        thirdpartie.embed_as.includes("ONVIEW")
    );
    const onClickThirdparties = props.newsletter?.third_parties.filter(thirdpartie =>
        thirdpartie.embed_as.includes("ONCLICK")
    );
    return (
        <div className="analysis">
            <h1>
                <Trans>analysis_analysis</Trans>
            </h1>
            <OnOpenThirdparties thirdparties={onOpenThirdparties} homeUrl={props.newsletter?.service.name} />
            <OnClickThirdparties thirdparties={onClickThirdparties} homeUrl={props.newsletter?.service.name} />
            <ABTesting newsletter={props.newsletter} />
        </div>
    );
};
export default Analysis;
