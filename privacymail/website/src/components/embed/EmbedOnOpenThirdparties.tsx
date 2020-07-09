import React from "react";
import { Trans } from "react-i18next";
import { IThirdParty, Reliability } from "../../repository";
import CollapsibleItem from "../../utils/CollapsibleItem";
import Methode from "../newsletter/analysis/Methode";
import ThirdpartyConnections from "../newsletter/analysis/ThirdpartyConnections";

interface OnOpenThirdpartiesProps {
    thirdparties?: IThirdParty[];
    homeUrl?: string;
    reliability?: Reliability;
}
/**
 * Defines how the ONOPEN analysis should look like
 */
const EmbedOnOpenThirdparties = (props: OnOpenThirdpartiesProps) => {
    return (
        <CollapsibleItem>
            <OnOpenThirdpartiesSmall {...props} />
            <OnOpenThirdpartiesBig {...props} />
        </CollapsibleItem>
    );
};
/**
 * Defines how the ONOPEN analysis preview should look like
 */
const OnOpenThirdpartiesSmall = (props: OnOpenThirdpartiesProps) => {
    return (
        <>
            <div className="summarizedInfo">{props.thirdparties?.length}</div>
            <div className="describeText">
                <Trans i18nKey={"embed_onopenThirdPartyShort"} count={props.thirdparties?.length} />
            </div>
        </>
    );
};
/**
 * Defines how the ONOPEN analysis expanded view should look like
 */
const OnOpenThirdpartiesBig = (props: OnOpenThirdpartiesProps) => {
    return (
        <>
            <h2>
                <Trans>embed_connections</Trans>
            </h2>
            <ThirdpartyConnections thirdparties={props.thirdparties} homeUrl={props.homeUrl} linkTo="/service" />

            <div className="divider" />
            <div>
                <h2>
                    <Trans>embed_problemHeadline</Trans>
                </h2>
                <p>
                    <Trans>embed_problemOnOpen</Trans>
                </p>
            </div>

            <div className="divider" />

            <Methode reliability={props.reliability} />
        </>
    );
};

export default EmbedOnOpenThirdparties;
