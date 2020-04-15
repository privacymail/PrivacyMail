import React from "react";
import { Trans } from "react-i18next";
import { IThirdParty, Reliability } from "../../repository";
import CollapsibleItem from "../../utils/CollapsibleItem";
import Methode from "../newsletter/analysis/Methode";
import ThirdpartyConnections from "../newsletter/analysis/ThirdpartyConnections";
import ColoredNumbers from "../newsletter/analysis/ColoredNumbers";

interface OnOpenThirdpartiesProps {
    thirdparties?: IThirdParty[];
    homeUrl?: string;
    reliability?: Reliability;
}

const EmbedOnOpenThirdparties = (props: OnOpenThirdpartiesProps) => {
    return (
        <CollapsibleItem>
            <OnOpenThirdpartiesSmall {...props} />
            <OnOpenThirdpartiesBig {...props} />
        </CollapsibleItem>
    );
};

const OnOpenThirdpartiesSmall = (props: OnOpenThirdpartiesProps) => {
    return (
        <div className="analysisSmall">
            <div className="summarizedInfo">
                <ColoredNumbers number={props.thirdparties?.length} />
            </div>
            <div className="describeText">
                <Trans>embed_onopenThirdPartyShort</Trans>
            </div>
        </div>
    );
};
const OnOpenThirdpartiesBig = (props: OnOpenThirdpartiesProps) => {
    return (
        <div className="analysisBig">
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

            <div className="divider" />
            <h2>
                <Trans>embed_connections</Trans>
                <ThirdpartyConnections thirdparties={props.thirdparties} homeUrl={props.homeUrl} linkTo="/service" />
            </h2>
        </div>
    );
};

export default EmbedOnOpenThirdparties;
