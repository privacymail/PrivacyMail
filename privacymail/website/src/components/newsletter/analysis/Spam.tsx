import React from "react";
import { Trans } from "react-i18next";
import { INewsletter, Reliability } from "../../../repository";
import PassOrNotIcon, { PassOrNotState } from "./PassOrNotIcon";
import Methode from "./Methode";
import CollapsibleItem from "../../../utils/CollapsibleItem";

interface SpamProps {
    newsletter?: INewsletter;
    reliability?: Reliability;
}

const Spam = (props: SpamProps) => {
    return (
        <CollapsibleItem>
            <SpamSmall newsletter={props.newsletter} />
            <SpamBig reliability={props.reliability} />
        </CollapsibleItem>
    );
};

const SpamSmall = (props: SpamProps) => {
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
