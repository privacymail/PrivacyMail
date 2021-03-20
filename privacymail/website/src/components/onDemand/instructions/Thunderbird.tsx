import React from "react";
import { Trans } from "react-i18next";

const Thunderbird = () => {
    return (
        <div className="instruction">
            <h3>
                <Trans>step</Trans> 2: <Trans>onDemand_step2_headline</Trans>
            </h3>
            <h4>
                <Trans>onDemand_thunderbird_step21</Trans>
            </h4>
            <img
                src={require("../../../assets/images/onDemandInstructions/thunderbirdViewSource.png")}
                alt="Thunderbird View Source Button"
            />
            <h4>
                <Trans>onDemand_thunderbird_step22</Trans>
            </h4>

            <img
                src={require("../../../assets/images/onDemandInstructions/thunderbirdCopyEmail.png")}
                alt="Thunderbird View Source Button"
            />
        </div>
    );
};

export default Thunderbird;
