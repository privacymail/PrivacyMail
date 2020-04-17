import React from "react";
import { Trans } from "react-i18next";

const WhatWeDo = () => {
    return (
        <div className="whatWeDo">
            <h2 className="grid-item regular">
                <Trans>home_shiningALight</Trans>
            </h2>
            <div className="grid-item">
                <p className="normal light">
                    <Trans>home_shiningALightDetail</Trans>
                </p>
            </div>
        </div>
    );
};
export default WhatWeDo;
