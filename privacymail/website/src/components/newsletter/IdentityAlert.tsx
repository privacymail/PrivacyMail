import React from "react";
import { Trans } from "react-i18next";
import { Link } from "react-router-dom";

interface IdentityAlertProps {
    newsletterName: string;
}

const IdentityAlert = (props: IdentityAlertProps) => {
    return (
        <div className="alert warning identityAlert">
            <p>
                <Trans>identity_lowIdentityCount</Trans>
            </p>
            <Link to={"/identity/" + props.newsletterName}>
                <button id="analizeButton">
                    <Trans>identity_addIdentity</Trans>
                </button>
            </Link>
        </div>
    );
};
export default IdentityAlert;
