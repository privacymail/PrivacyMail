import React from "react";
import { Trans } from "react-i18next";
import { INewsletter } from "../../../repository";
import OnOpenThirdparties from "./OnOpenThirdparties";
import OnClickThirdparties from "./OnClickThirdparties";
import ABTesting from "./ABTesting";
import Spam from "./Spam";
import PersonalisedLinks from "./PersonalisedLinks";

interface AnalysisProps {
    newsletter?: INewsletter;
}

/**
 * Defines the Analysis
 */
const Analysis = (props: AnalysisProps) => {
    //Filters all ONVIEW Thirdparties
    const onOpenThirdparties = props.newsletter?.third_parties.filter(thirdpartie =>
        thirdpartie.embed_as.includes("ONVIEW")
    );

    //Filters all ONCLICK Thirdparties
    const onClickThirdparties = props.newsletter?.third_parties.filter(thirdpartie =>
        thirdpartie.embed_as.includes("ONCLICK")
    );
    return (
        <div className="analysis">
            <h1>
                <Trans>analysis_analysis</Trans>
            </h1>
            <OnOpenThirdparties
                thirdparties={onOpenThirdparties}
                homeUrl={props.newsletter?.service.name}
                reliability={props.newsletter?.reliability.mailOpen}
            />
            <OnClickThirdparties
                thirdparties={onClickThirdparties}
                homeUrl={props.newsletter?.service.name}
                reliability={props.newsletter?.reliability.linkClicked}
            />
            <PersonalisedLinks
                newsletter={props.newsletter}
                reliability={props.newsletter?.reliability.personalisedLinks}
            />
            <ABTesting newsletter={props.newsletter} reliability={props.newsletter?.reliability.abTesting} />
            <Spam newsletter={props.newsletter} reliability={props.newsletter?.reliability.spam} />
        </div>
    );
};
export default Analysis;
