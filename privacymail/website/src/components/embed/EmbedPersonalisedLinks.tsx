import React from "react";
import { Trans } from "react-i18next";
import { IThirdParty, Reliability, INewsletter, IEmbed } from "../../repository";
import CollapsibleItem from "../../utils/CollapsibleItem";
import Methode from "../newsletter/analysis/Methode";
import PassOrNotIcon, { PassOrNotState } from "../newsletter/analysis/PassOrNotIcon";

interface PersonalisedLinksProps {
    newsletter?: INewsletter | IEmbed;
    reliability?: Reliability;
}

const EmbedPersonalisedLinks = (props: PersonalisedLinksProps) => {
    return (
        <CollapsibleItem>
            <PersonalisedLinksSmall newsletter={props.newsletter} />
            <PersonalisedLinksBig reliability={props.reliability} />
        </CollapsibleItem>
    );
};

const PersonalisedLinksSmall = (props: PersonalisedLinksProps) => {
    const getStatus = (third_parties: IThirdParty[] | undefined) => {
        if (
            third_parties &&
            third_parties.length >= 1 &&
            third_parties.find((elem: IThirdParty) => elem.address_leak_click || elem.address_leak_view)
        ) {
            return PassOrNotState.Denied;
        } else {
            return PassOrNotState.Passed;
        }
    };
    const newsletter = props.newsletter as any;
    const status = getStatus(newsletter?.third_parties || newsletter?.services);
    return (
        <div className="analysisSmall">
            <PassOrNotIcon status={status} className="passOrNot summarizedInfo" />
            <div className="describeText">
                {status === PassOrNotState.Passed ? (
                    <Trans>embed_PersonalisedLinks_no</Trans>
                ) : (
                    <Trans>embed_PersonalisedLinks</Trans>
                )}
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
                    <Trans>embed_problemHeadline</Trans>
                </h2>
                <p>
                    <Trans>embed_PersonalisedLinks_problem</Trans>
                </p>
            </div>

            <div className="divider" />

            <Methode reliability={props.reliability} />
        </div>
    );
};

export default EmbedPersonalisedLinks;
