import React from "react";
import { Trans } from "react-i18next";
import { IThirdParty, Reliability } from "../../../repository";
import Methode from "./Methode";
import CollapsibleItem from "../../../utils/CollapsibleItem";
import ThridpartysByCategory from "./ThridpartysByCategory";
import ColoredNumbers from "./ColoredNumbers";
import { areThirdpartiesEvil } from "../../../utils/functions/isThirdpartyEvil";

interface OnOpenThirdpartiesProps {
    thirdparties?: IThirdParty[];
    homeUrl?: string;
    reliability?: Reliability;
}

const OnOpenThirdparties = (props: OnOpenThirdpartiesProps) => {
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
                <ColoredNumbers
                    number={props.thirdparties?.length}
                    pow={areThirdpartiesEvil(props.thirdparties) ? 0.9 : 0.5}
                />
            </div>
            <div className="describeText">
                <Trans>analysis_onopenThirdPartyShort</Trans>
            </div>
        </div>
    );
};
const OnOpenThirdpartiesBig = (props: OnOpenThirdpartiesProps) => {
    return (
        <div className="analysisBig">
            <h2>
                <Trans>analysis_connections</Trans>
            </h2>
            <ThridpartysByCategory thirdparties={props.thirdparties} homeUrl={props.homeUrl} />

            <div className="divider" />
            <div>
                <h2>
                    <Trans>analysis_problemHeadline</Trans>
                </h2>
                <p>
                    <Trans>analysis_problemOnOpen</Trans>
                </p>
            </div>

            <div className="divider" />

            <Methode reliability={props.reliability} />
        </div>
    );
};

export default OnOpenThirdparties;
