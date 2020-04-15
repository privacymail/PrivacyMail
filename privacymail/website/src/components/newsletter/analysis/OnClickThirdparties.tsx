import React from "react";
import { Trans } from "react-i18next";
import { IThirdParty, Reliability } from "../../../repository";
import ThirdpartyConnections from "./ThirdpartyConnections";
import Methode from "./Methode";
import CollapsibleItem from "../../../utils/CollapsibleItem";
import ColoredNumbers from "./ColoredNumbers";

interface OnClickThirdpartiesProps {
    thirdparties?: IThirdParty[];
    homeUrl?: string;
    reliability?: Reliability;
}

const OnClickThirdparties = (props: OnClickThirdpartiesProps) => {
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
            <div className="summarizedInfo">
                <ColoredNumbers number={props.thirdparties?.length} />
            </div>
            <div className="describeText">
                <Trans>analysis_onclickThirdPartyShort</Trans>
            </div>
        </div>
    );
};
const OnClickThirdpartiesBig = (props: OnClickThirdpartiesProps) => {
    return (
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

            <Methode reliability={props.reliability} />

            <div className="divider" />
            <h2>
                <Trans>analysis_connections</Trans>
                <ThirdpartyConnections thirdparties={props.thirdparties} homeUrl={props.homeUrl} />
            </h2>
        </div>
    );
};

export default OnClickThirdparties;
