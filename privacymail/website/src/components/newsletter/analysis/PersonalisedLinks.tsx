import React from "react";
import { Trans } from "react-i18next";
import { INewsletter, Reliability, IThirdParty, IEmbed } from "../../../repository";
import PassOrNotIcon, { PassOrNotState } from "./PassOrNotIcon";
import Methode from "./Methode";
import CollapsibleItem from "../../../utils/CollapsibleItem";

interface PersonalisedLinksProps {
    newsletter?: INewsletter | IEmbed;
    reliability?: Reliability;
}
/**
 * Defines how the PersonalisedLinks analysis should look like
 */
const PersonalisedLinks = (props: PersonalisedLinksProps) => {
    return (
        <CollapsibleItem>
            <PersonalisedLinksSmall newsletter={props.newsletter} />
            <PersonalisedLinksBig reliability={props.reliability} />
        </CollapsibleItem>
    );
};
/**
 * Defines how the PersonalisedLinks analysis preview should look like
 */
const PersonalisedLinksSmall = (props: PersonalisedLinksProps) => {
    const getStatus = (third_parties: IThirdParty[] | undefined) => {
        if (
            third_parties &&
            third_parties.length >= 1 &&
            third_parties.find(
                (elem: IThirdParty) => elem.address_leak_click || elem.address_leak_view || elem.receives_identifier
            )
        ) {
            return PassOrNotState.Denied;
        } else {
            return PassOrNotState.Passed;
        }
    };
    const newsletter = props.newsletter as any;
    const status = getStatus(newsletter?.third_parties || newsletter?.services);
    return (
        <>
            <PassOrNotIcon status={status} className="passOrNot summarizedInfo" />
            <div className="describeText">
                {status === PassOrNotState.Passed ? (
                    <Trans>analysis_PersonalisedLinks_no</Trans>
                ) : (
                    <Trans>analysis_PersonalisedLinks</Trans>
                )}
            </div>
        </>
    );
};

interface PersonalisedLinksBigProps {
    reliability?: Reliability;
}
/**
 * Defines how the PersonalisedLinks analysis expanded view should look like
 */
const PersonalisedLinksBig = (props: PersonalisedLinksBigProps) => {
    return (
        <>
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
        </>
    );
};

export default PersonalisedLinks;
