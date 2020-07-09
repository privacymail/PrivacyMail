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
/**
 * Defines how the ONVIEW analysis should look like
 */
const OnOpenThirdparties = (props: OnOpenThirdpartiesProps) => {
    return (
        <CollapsibleItem>
            <OnOpenThirdpartiesSmall {...props} />
            <OnOpenThirdpartiesBig {...props} />
        </CollapsibleItem>
    );
};
/**
 * Defines how the ONVIEW analysis preview should look like
 */
const OnOpenThirdpartiesSmall = (props: OnOpenThirdpartiesProps) => {
    return (
        <>
            <div className="summarizedInfo">
                <ColoredNumbers
                    number={props.thirdparties?.length}
                    pow={areThirdpartiesEvil(props.thirdparties) ? 0.9 : 0.5}
                />
            </div>
            <div className="describeText">
                <Trans i18nKey={"analysis_onopenThirdPartyShort"} count={props.thirdparties?.length} />
            </div>
        </>
    );
};
/**
 * Defines how the ONVIEW analysis expanded view should look like
 */
const OnOpenThirdpartiesBig = (props: OnOpenThirdpartiesProps) => {
    return (
        <>
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
        </>
    );
};

export default OnOpenThirdparties;
