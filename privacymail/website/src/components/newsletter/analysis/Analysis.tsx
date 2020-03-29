import React from "react";
import { Trans } from "react-i18next";
import { INewsletter } from "../../../repository";
import OnOpenThirdparties from "./OnOpenThirdparties";
import OnClickThirdparties from "./OnClickThirdparties";

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
                <Trans>analysis</Trans>
            </h1>
            <OnOpenThirdparties thirdparties={onOpenThirdparties} />
            <OnClickThirdparties thirdparties={onClickThirdparties} />
            {/* <ABTesting />
            <Spam /> */}
        </div>
    );
};
export default Analysis;
