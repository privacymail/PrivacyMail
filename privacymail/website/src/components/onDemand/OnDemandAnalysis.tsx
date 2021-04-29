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
        <>
            {!props.emailAnalysis && (
                <div className="alert warning">
                    <Trans>onDemand_warning</Trans>
                </div>
            )}
            <Spinner isSpinning={!props.emailAnalysis}>
                <div className="analysis">
                    <OnOpenThirdparties
                        thirdparties={props.emailAnalysis?.third_parties}
                        homeUrl={props.emailAnalysis?.homeUrl}
                    />
                    <PersonalisedLinks mailLeakage={props.emailAnalysis?.mailLeakage} />
                    <Cookies {...props} />

                    <div className="buttonRight">
                        <button
                            onClick={e => {
                                props.returnToInput();
                            }}
                        >
                            <Trans>onDemand_newAnalysis</Trans>
                        </button>
                    </div>
                </div>
            </Spinner>
        </>
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
                    {status === PassOrNotState.Passed ? <Trans>sets_no_cookies</Trans> : <Trans>sets_cookies</Trans>}
                </div>
            </div>
        </div>
    );
};

export default OnDemandAnalysis;
