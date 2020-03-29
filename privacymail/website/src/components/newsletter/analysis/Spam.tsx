import React from "react";
import { Trans } from "react-i18next";
import { INewsletter } from "../../../repository";

interface SpamProps {
    newsletter?: INewsletter;
}

const Spam = (props: SpamProps) => {
    return (
        <div className="generalInfo">
            <h1>
                <Trans>analysis_analysis</Trans>
            </h1>
        </div>
    );
};
export default Spam;
