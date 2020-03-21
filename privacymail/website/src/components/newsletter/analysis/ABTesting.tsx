import React from "react";
import { Trans } from "react-i18next";
import { INewsletter } from "../../../repository";

interface ABTestingProps {
    newsletter?: INewsletter;
}

const ABTesting = (props: ABTestingProps) => {
    return (
        <div className="generalInfo">
            <h1>
                <Trans>analysis</Trans>
            </h1>
        </div>
    );
};
export default ABTesting;
