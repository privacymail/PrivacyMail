import React from "react";
import { Trans } from "react-i18next";
import { INewsletter, Reliability } from "../../../repository";
import PassOrNotIcon, { PassOrNotState } from "./PassOrNotIcon";
import Methode from "./Methode";
import CollapsibleItem from "../../../utils/CollapsibleItem";

interface ABTestingProps {
    newsletter?: INewsletter;
    reliability?: Reliability;
}
/**
 * A/B-Testing Analasis
 */
const ABTesting = (props: ABTestingProps) => {
    return (
        <CollapsibleItem>
            <ABTestingSmall newsletter={props.newsletter} />
            <ABTestingBig reliability={props.reliability} />
        </CollapsibleItem>
    );
};
/**
 * A/B-Testing Preview
 */
const ABTestingSmall = (props: ABTestingProps) => {
    const getStatus = (newsletter: INewsletter | undefined) => {
        if (newsletter?.num_different_idents && newsletter?.num_different_idents < 2) {
            return PassOrNotState.Disabled;
        } else if (newsletter?.suspected_AB_testing === false) {
            return PassOrNotState.Passed;
        } else if (newsletter?.suspected_AB_testing === true) {
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
                {status === PassOrNotState.Passed ? (
                    <Trans>analysis_abtesting_no</Trans>
                ) : status === PassOrNotState.Disabled ? (
                    <Trans>analysis_abtesting_disabled</Trans>
                ) : (
                    <Trans>analysis_abtesting</Trans>
                )}
            </div>
        </>
    );
};

interface ABTestingBigProps {
    reliability?: Reliability;
}
/**
 * A/B-Testing Detailed
 */
const ABTestingBig = (props: ABTestingBigProps) => {
    return (
        <>
            <div>
                <h2>
                    <Trans>analysis_problemHeadline</Trans>
                </h2>
                <p>
                    <Trans>analysis_abtesting_problem</Trans>
                </p>
            </div>

            <div className="divider" />

            <Methode reliability={props.reliability} textId={"analysis_reliability_abTesting"} />
        </>
    );
};

export default ABTesting;
