import React from "react";
import { IEmailAnalysis } from "../../repository";
import PassOrNotIcon, { PassOrNotState } from "../newsletter/analysis/PassOrNotIcon";
import OnOpenThirdparties from "../newsletter/analysis/OnOpenThirdparties";
import PersonalisedLinks from "../newsletter/analysis/PersonalisedLinks";
import { Trans } from "react-i18next";
import Spinner from "../../utils/Spinner";

interface OnDemandAnalysisProps {
    emailAnalysis?: IEmailAnalysis;
    returnToInput: () => void;
}

const OnDemandAnalysis = (props: OnDemandAnalysisProps) => {
    return (
        <Spinner isSpinning={!props.emailAnalysis}>
            <div className="analysis">
                <OnOpenThirdparties
                    thirdparties={props.emailAnalysis?.third_parties}
                    homeUrl={props.emailAnalysis?.homeUrl}
                />
                <PersonalisedLinks mailLeakage={props.emailAnalysis?.mailLeakage} />
                <Cookies {...props} />
                <button
                    onClick={() => {
                        props.returnToInput();
                    }}
                >
                    Return
                </button>
            </div>
        </Spinner>
    );
};

const Cookies = (props: OnDemandAnalysisProps) => {
    const getStatus = (setsCookies: boolean) => {
        if (setsCookies) return PassOrNotState.Denied;
        else return PassOrNotState.Passed;
    };
    const status = getStatus(props.emailAnalysis?.cookies ?? false);
    return (
        <div className="collapsibleItem">
            <div className="collapsibleSmall">
                <PassOrNotIcon status={status} className="passOrNot summarizedInfo" />
                <div className="describeText">
                    {status === PassOrNotState.Passed ? <Trans>Sets No Cookies</Trans> : <Trans>Sets Cookies</Trans>}
                </div>
            </div>
        </div>
    );
};

export default OnDemandAnalysis;
