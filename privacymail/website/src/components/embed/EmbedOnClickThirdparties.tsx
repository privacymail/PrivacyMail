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

const EmbedOnClickThirdparties = (props: OnClickThirdpartiesProps) => {
    return (
        <CollapsibleItem>
            <OnClickThirdpartiesSmall {...props} />
            <OnClickThirdpartiesBig {...props} />
        </CollapsibleItem>
    );
};

const OnClickThirdpartiesSmall = (props: OnClickThirdpartiesProps) => {
    return (
        <div className="analysisSmall">
            <div className="summarizedInfo">{props.thirdparties?.length}</div>
            <div className="describeText">
                <Trans>embed_onclickThirdPartyShort</Trans>
            </div>
        </div>
    );
};
const OnClickThirdpartiesBig = (props: OnClickThirdpartiesProps) => {
    return (
        <div className="analysisBig">
            <div>
                <h2>
                    <Trans>embed_problemHeadline</Trans>
                </h2>
                <p>
                    <Trans>embed_problemOnClick</Trans>
                </p>
            </div>

            <div className="divider" />

            <Methode reliability={props.reliability} />

            <div className="divider" />
            <h2>
                <Trans>embed_connections</Trans>
                <ThirdpartyConnections thirdparties={props.thirdparties} homeUrl={props.homeUrl} linkTo="/service" />
            </h2>
        </div>
    );
};

export default EmbedOnClickThirdparties;
