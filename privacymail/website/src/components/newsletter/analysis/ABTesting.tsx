import React, { useState } from "react";
import { Trans } from "react-i18next";
import { INewsletter } from "../../../repository";
import Collapsible from "react-collapsible";
import { Icon } from "../../../utils/Icon";
import PassOrNotIcon from "./PassOrNotIcon";

interface ABTestingProps {
    newsletter?: INewsletter;
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
                <div className="analysisBig">
                    <div>
                        <h2>
                            <Trans>analysis_problemHeadline</Trans>
                        </h2>
                        <p>
                            <Trans>analysis_problemOnClick</Trans>
                        </p>
                    </div>

                    <div className="divider" />

                    <div>
                        <h2>
                            <Trans>analysis_methode</Trans>
                        </h2>
                        <div className="methodeChip reliable">
                            <Trans>analysis_reliable</Trans>
                        </div>
                        <div className="methodeChip reliable">
                            <Trans>analysis_noPotentialMistakes</Trans>
                        </div>
                    </div>
                </div>
            </Collapsible>
        </div>
    );
};

interface ABTestingSmallProps extends ABTestingProps {
    expanded: boolean;
}
const ABTestingSmall = (props: ABTestingSmallProps) => {
    return (
        <div className="analysisSmall">
            <PassOrNotIcon passed={true} className="passOrNot summarizedInfo" />
            <div className="describeText">
                <Trans>analysis_abtesting</Trans>
            </div>
            <div className="expandable">
                <Icon className={props.expanded ? " expanded" : " closed"}>expand</Icon>
            </div>
        </div>
    );
};

export default ABTesting;
