import React from "react";
import { Trans } from "react-i18next";
import { IThirdParty } from "../../../repository";

interface OnOpenThirdpartiesProps {
    thirdparties?: IThirdParty[];
}

const OnOpenThirdparties = (props: OnOpenThirdpartiesProps) => {
    return (
        <div className="generalInfo">
            <h1>
                <Trans>analysis</Trans>
            </h1>
        </div>
    );
};
export default OnOpenThirdparties;
