import React from "react";
import { Trans } from "react-i18next";

const DefaultNotFound = () => {
    return (
        <div className="notFound">
            <div className="heading thin">
                <Trans>404_heading</Trans>
            </div>
            <div className="light">
                <Trans>404_message3</Trans>
            </div>
        </div>
    );
};
export default DefaultNotFound;
