import React from "react";
import { Trans } from "react-i18next";
import { Reliability } from "../../../repository";

interface MethodeProps {
    reliability?: Reliability;
    textId?: string;
}
/**
 * Displays the methode part of the big few of the analysis items
 */
const Methode = (props: MethodeProps) => {
    return (
        <div>
            <h2>
                <Trans>analysis_methode</Trans>
            </h2>
            {props.reliability && (
                <div className={"methodeChip " + props.reliability}>
                    <Trans>analysis_{props.reliability}</Trans>
                </div>
            )}
            {props.textId && (
                <div className="reliablityText">
                    <Trans>{props.textId}</Trans>
                </div>
            )}
        </div>
    );
};

export default Methode;
