import React, { useState } from "react";
import { Trans } from "react-i18next";
import { INewsletter, Reliability, IThirdParty } from "../../../repository";
import Collapsible from "react-collapsible";
import { Icon } from "../../../utils/Icon";
import PassOrNotIcon, { PassOrNotState } from "./PassOrNotIcon";
import Methode from "./Methode";

interface PersonalisedLinksProps {
    newsletter?: INewsletter;
    reliability?: Reliability;
}

const PersonalisedLinks = (props: PersonalisedLinksProps) => {
    const [isExpanded, setIsExpanded] = useState(false);

    return (
        <div className="analysisItem">
            <Collapsible
                onOpening={() => setIsExpanded(true)}
                onClosing={() => setIsExpanded(false)}
                trigger={<PersonalisedLinksSmall newsletter={props.newsletter} expanded={isExpanded} />}
            >
                <PersonalisedLinksBig reliability={props.reliability} />
            </Collapsible>
        </div>
    );
};

interface PersonalisedLinksSmallProps extends PersonalisedLinksProps {
    expanded: boolean;
}
const PersonalisedLinksSmall = (props: PersonalisedLinksSmallProps) => {
    const getStatus = (newsletter: INewsletter | undefined) => {
        if (
            newsletter &&
            newsletter?.third_parties.length >= 1 &&
            newsletter?.third_parties.find((elem: IThirdParty) => elem.address_leak_click || elem.address_leak_view)
        ) {
            return PassOrNotState.Denied;
        } else {
            return PassOrNotState.Passed;
        }
    };
    const status = getStatus(props.newsletter);
    return (
        <div className="analysisSmall">
            <PassOrNotIcon status={status} className="passOrNot summarizedInfo" />
            <div className="describeText">
                {status === PassOrNotState.Passed ? (
                    <Trans>analysis_PersonalisedLinks_no</Trans>
                ) : (
                    <Trans>analysis_PersonalisedLinks</Trans>
                )}
            </div>
            <div className="expandable">
                <Icon className={props.expanded ? " expanded" : " closed"}>expand</Icon>
            </div>
        </div>
    );
};

interface PersonalisedLinksBigProps {
    reliability?: Reliability;
}
const PersonalisedLinksBig = (props: PersonalisedLinksBigProps) => {
    return (
        <div className="analysisBig">
            <div>
                <h2>
                    <Trans>analysis_problemHeadline</Trans>
                </h2>
                <p>
                    <Trans>analysis_PersonalisedLinks_problem</Trans>
                </p>
            </div>

            <div className="divider" />

            <Methode reliability={props.reliability} />
        </div>
    );
};

export default PersonalisedLinks;
