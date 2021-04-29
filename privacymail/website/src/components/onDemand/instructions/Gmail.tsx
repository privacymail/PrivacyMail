import React from "react";
import { Trans } from "react-i18next";

const Gmail = () => {
    return (
        <div className="instruction">
            <h3>
                <Trans>step</Trans> 2: <Trans>onDemand_step2_headline</Trans>
            </h3>
            <h4>
                <Trans>onDemand_gmail_step21</Trans>
            </h4>
            <img
                src={require("../../../assets/images/onDemandInstructions/gmailViewSource.png")}
                alt="Thunderbird View Source Button"
            />
            <h4>
                <Trans>onDemand_gmail_step22</Trans>
            </h4>

            <img
                src={require("../../../assets/images/onDemandInstructions/gmailCopyEmail.png")}
                alt="Thunderbird View Source Button"
            />
        </div>
    );
};

export default Gmail;
