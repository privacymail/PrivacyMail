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
/**
 * Defines how the Spam analysis should look like
 */
const Spam = (props: SpamProps) => {
    return (
        <CollapsibleItem>
            <SpamSmall newsletter={props.newsletter} />
            <SpamBig reliability={props.reliability} />
        </CollapsibleItem>
    );
};
/**
 * Defines how the Spam analysis should look like
 */
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
        <>
            <PassOrNotIcon status={status} className="passOrNot summarizedInfo" />
            <div className="describeText">
                {status === PassOrNotState.Passed ? <Trans>analysis_Spam_no</Trans> : <Trans>analysis_Spam</Trans>}
            </div>
        </>
    );
};

interface SpamBigProps {
    reliability?: Reliability;
}
/**
 * Defines how the Spam analysis should look like
 */
const SpamBig = (props: SpamBigProps) => {
    return (
        <>
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
        </>
    );
};

export default Spam;
