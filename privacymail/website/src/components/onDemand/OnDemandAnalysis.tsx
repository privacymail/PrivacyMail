import React from "react";
import { IEmailAnalysis } from "../../repository";
import CollapsibleItem from "../../utils/CollapsibleItem";
import ColoredNumbers from "../newsletter/analysis/ColoredNumbers";
import PassOrNotIcon, { PassOrNotState } from "../newsletter/analysis/PassOrNotIcon";
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
                <CollapsibleItem>
                    <EresourcesSmall {...props} />
                    <EresourcesBig {...props} />
                </CollapsibleItem>
                <CollapsibleItem>
                    <LeakageSmall {...props} />
                    <LeakageBig {...props} />
                </CollapsibleItem>
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

const EresourcesSmall = (props: OnDemandAnalysisProps) => {
    return (
        <>
            <div className="summarizedInfo">
                <ColoredNumbers
                    number={props.emailAnalysis?.eresources_on_view}
                    pow={props.emailAnalysis && props.emailAnalysis?.leak_eresource_set_count > 0 ? 0.9 : 0.5}
                />
            </div>
            <div className="describeText">Links opened on viewing the Email</div>
        </>
    );
};

const EresourcesBig = (props: OnDemandAnalysisProps) => {
    return (
        <>
            <h2>
                <Trans>analysis_connections</Trans>
            </h2>
            <div className="divider" />
            <div className="connections">
                <div className="category">
                    <ColoredNumbers number={props.emailAnalysis?.directly_embedded_eresources} />
                    <div className="name">directly embedded links</div>
                </div>
                <CollapsibleItem>
                    <ThirdPartySmall {...props} />
                    <ThirdPartyBig {...props} />
                </CollapsibleItem>
                <CollapsibleItem>
                    <AdditionalThirdPartySmall {...props} />
                    <AdditionalThirdPartyBig {...props} />
                </CollapsibleItem>
            </div>
        </>
    );
};

const ThirdPartySmall = (props: OnDemandAnalysisProps) => {
    return (
        <div className="category">
            <ColoredNumbers number={props.emailAnalysis?.directly_embedded_third_party} />
            <div className="name">third party</div>
        </div>
    );
};

const ThirdPartyBig = (props: OnDemandAnalysisProps) => {
    return (
        <ul>
            {props.emailAnalysis?.third_parties.map(thirdparty => (
                <li key={thirdparty}>{thirdparty}</li>
            ))}
            <li></li>
        </ul>
    );
};

const AdditionalThirdPartySmall = (props: OnDemandAnalysisProps) => {
    return (
        <div className="category">
            <ColoredNumbers number={props.emailAnalysis?.directly_embedded_third_party} />
            <div className="name">additional loaded links to third parties</div>
        </div>
    );
};

const AdditionalThirdPartyBig = (props: OnDemandAnalysisProps) => {
    return (
        <ul>
            {props.emailAnalysis?.additionaly_loaded_parties.map(thirdparty => (
                <li key={thirdparty}>{thirdparty}</li>
            ))}
            <li></li>
        </ul>
    );
};

const LeakageSmall = (props: OnDemandAnalysisProps) => {
    return (
        <>
            <div className="summarizedInfo">
                <ColoredNumbers number={props.emailAnalysis?.leak_eresource_set_count} />
            </div>
            <div className="describeText">
                <div className="name">links leaked your Email address</div>
            </div>
        </>
    );
};

const LeakageBig = (props: OnDemandAnalysisProps) => {
    return (
        <div className="connections">
            <div className="collapsibleItem">
                <div className="collapsibleSmall">
                    <div className="category">
                        <ColoredNumbers number={props.emailAnalysis?.num_of_leaks_to_third_parties} />
                        <div className="name">leak Email to third party providers</div>
                    </div>
                </div>
            </div>
            <div className="collapsibleItem">
                <div className="collapsibleSmall">
                    <div className="category">
                        <ColoredNumbers number={props.emailAnalysis?.num_of_leaks_through_forwards} />
                        <div className="name">leak Email through forwards</div>
                    </div>
                </div>
            </div>
            {props.emailAnalysis && props.emailAnalysis.leak_eresource_set_count > 0 && (
                <>
                    <h2>Leaking methods</h2>
                    <ul>
                        {props.emailAnalysis?.leaking_methods.map(method => (
                            <li key={method}>{method}</li>
                        ))}
                        <li></li>
                    </ul>
                </>
            )}
            <div>
                <h2>
                    <Trans>analysis_problemHeadline</Trans>
                </h2>
                <p>
                    <Trans>analysis_problemOnOpen</Trans>
                </p>
            </div>
        </div>
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
