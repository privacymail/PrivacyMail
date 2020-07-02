import React from "react";
import { Trans } from "react-i18next";
import { IThirdParty, Reliability } from "../../../repository";
import Methode from "./Methode";
import CollapsibleItem from "../../../utils/CollapsibleItem";
import ColoredNumbers from "./ColoredNumbers";
import ThridpartysByCategory from "./ThridpartysByCategory";
import { areThirdpartiesEvil } from "../../../utils/functions/isThirdpartyEvil";

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
        <>
            <div className="summarizedInfo">
                <ColoredNumbers
                    number={props.thirdparties?.length}
                    pow={areThirdpartiesEvil(props.thirdparties) ? 0.9 : 0.1}
                />
            </div>
            <div className="describeText">
                <Trans>analysis_onclickThirdPartyShort</Trans>
            </div>
        </>
    );
};
const OnClickThirdpartiesBig = (props: OnClickThirdpartiesProps) => {
    return (
        <>
            <h2>
                <Trans>analysis_connections</Trans>
            </h2>
            <ThridpartysByCategory thirdparties={props.thirdparties} homeUrl={props.homeUrl} defaultPow={0.1} />
            <div className="divider" />
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
        </>
    );
};

export default OnClickThirdparties;
