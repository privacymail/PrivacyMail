import React, { useState } from "react";
import { Trans } from "react-i18next";
import { INewsletter, Reliability } from "../../../repository";
import Collapsible from "react-collapsible";
import { Icon } from "../../../utils/Icon";
import PassOrNotIcon, { PassOrNotState } from "./PassOrNotIcon";
import Methode from "./Methode";

interface ABTestingProps {
    newsletter?: INewsletter;
    reliability?: Reliability;
}

const ABTesting = (props: ABTestingProps) => {
    const [isExpanded, setIsExpanded] = useState(false);

    return (
        <div className="analysisItem">
            <Collapsible
                onOpening={() => setIsExpanded(true)}
                onClosing={() => setIsExpanded(false)}
                trigger={<ABTestingSmall newsletter={props.newsletter} expanded={isExpanded} />}
            >
                <ABTestingBig reliability={props.reliability} />
            </Collapsible>
        </div>
    );
};

interface ABTestingSmallProps extends ABTestingProps {
    expanded: boolean;
}
const ABTestingSmall = (props: ABTestingSmallProps) => {
    const getStatus = (newsletter: INewsletter | undefined) => {
        if (newsletter?.num_different_idents && newsletter?.num_different_idents <= 2) {
            return PassOrNotState.Disabled;
        } else if (newsletter?.suspected_AB_testing === false) {
            return PassOrNotState.Passed;
        } else if (newsletter?.suspected_AB_testing === true) {
            return PassOrNotState.Denied;
        } else {
            return undefined;
        }
    };

    return (
        <div className="analysisSmall">
            <PassOrNotIcon status={getStatus(props.newsletter)} className="passOrNot summarizedInfo" />
            <div className="describeText">
                <Trans>analysis_abtesting</Trans>
            </div>
            <div className="expandable">
                <Icon className={props.expanded ? " expanded" : " closed"}>expand</Icon>
            </div>
        </div>
    );
};

interface ABTestingBigProps {
    reliability?: Reliability;
}
const ABTestingBig = (props: ABTestingBigProps) => {
    return (
        <div className="analysisBig">
            <div>
                <h2>
                    <Trans>analysis_problemHeadline</Trans>
                </h2>
                <p>
                    <Trans>analysis_abtesting_problem</Trans>
                </p>
            </div>

            <div className="divider" />

            <Methode reliability={props.reliability} />
        </div>
    );
};

export default ABTesting;
