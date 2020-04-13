import React, { useState } from "react";
import { Trans } from "react-i18next";
import { INewsletter, Reliability } from "../../../repository";
import Collapsible from "react-collapsible";
import { Icon } from "../../../utils/Icon";
import PassOrNotIcon, { PassOrNotState } from "./PassOrNotIcon";
import Methode from "./Methode";

interface SpamProps {
    newsletter?: INewsletter;
    reliability?: Reliability;
}

const Spam = (props: SpamProps) => {
    const [isExpanded, setIsExpanded] = useState(false);

    return (
        <div className="analysisItem">
            <Collapsible
                onOpening={() => setIsExpanded(true)}
                onClosing={() => setIsExpanded(false)}
                trigger={<SpamSmall newsletter={props.newsletter} expanded={isExpanded} />}
            >
                <SpamBig reliability={props.reliability} />
            </Collapsible>
        </div>
    );
};

interface SpamSmallProps extends SpamProps {
    expanded: boolean;
}
const SpamSmall = (props: SpamSmallProps) => {
    const getStatus = (newsletter: INewsletter | undefined) => {
        if (newsletter?.third_party_spam === 0) {
            return PassOrNotState.Passed;
        } else if (newsletter?.third_party_spam !== 0) {
            return PassOrNotState.Denied;
        } else {
            return undefined;
        }
    };
    const status = getStatus(props.newsletter);
    return (
        <div className="analysisSmall">
            <PassOrNotIcon status={status} className="passOrNot summarizedInfo" />
            <div className="describeText">
                {status === PassOrNotState.Passed ? <Trans>analysis_Spam_no</Trans> : <Trans>analysis_Spam</Trans>}
            </div>
            <div className="expandable">
                <Icon className={props.expanded ? " expanded" : " closed"}>expand</Icon>
            </div>
        </div>
    );
};

interface SpamBigProps {
    reliability?: Reliability;
}
const SpamBig = (props: SpamBigProps) => {
    return (
        <div className="analysisBig">
            <div>
                <h2>
                    <Trans>analysis_problemHeadline</Trans>
                </h2>
                <p>
                    <Trans>analysis_Spam_problem</Trans>
                </p>
            </div>

            <div className="divider" />

            <Methode reliability={props.reliability} />
        </div>
    );
};

export default Spam;
