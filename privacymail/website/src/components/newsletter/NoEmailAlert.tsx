import React from "react";
import { Trans } from "react-i18next";
import { Link } from "react-router-dom";

interface NoEmailAlertProps {
    newsletterName: string;
}

const NoEmailAlert = (props: NoEmailAlertProps) => {
    return (
        <div className="alert warning identityAlert">
            <p>
                <Trans>analysis_noEmailsReceived</Trans>
            </p>
            <Link to={"/identity/" + props.newsletterName}>
                <button id="analizeButton">
                    <Trans>identity_addIdentity</Trans>
                </button>
            </Link>
        </div>
    );
};
export default NoEmailAlert;
