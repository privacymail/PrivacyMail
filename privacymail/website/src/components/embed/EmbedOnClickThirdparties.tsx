import React from "react";
import { Trans } from "react-i18next";
import { IThirdParty, Reliability } from "../../repository";
import CollapsibleItem from "../../utils/CollapsibleItem";
import Methode from "../newsletter/analysis/Methode";
import ThirdpartyConnections from "../newsletter/analysis/ThirdpartyConnections";
interface OnClickThirdpartiesProps {
    thirdparties?: IThirdParty[];
    homeUrl?: string;
    reliability?: Reliability;
}
/**
 * Defines how the ONCLICK analysis should look like
 */
const EmbedOnClickThirdparties = (props: OnClickThirdpartiesProps) => {
    return (
        <CollapsibleItem>
            <OnClickThirdpartiesSmall {...props} />
            <OnClickThirdpartiesBig {...props} />
        </CollapsibleItem>
    );
};
/**
 * Defines how the ONCLICK analysis preview should look like
 */
const OnClickThirdpartiesSmall = (props: OnClickThirdpartiesProps) => {
    return (
        <>
            <div className="summarizedInfo">{props.thirdparties?.length}</div>
            <div className="describeText">
                <Trans i18nKey={"embed_onclickThirdPartyShort"} count={props.thirdparties?.length} />
            </div>
        </>
    );
};
/**
 * Defines how the ONCLICK analysis expanded view should look like
 */
const OnClickThirdpartiesBig = (props: OnClickThirdpartiesProps) => {
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
                    <Trans>embed_problemOnClick</Trans>
                </p>
            </div>

            <div className="divider" />

            <Methode reliability={props.reliability} textId={"analysis_reliability_onClick"} />
        </>
    );
};

export default EmbedOnClickThirdparties;
