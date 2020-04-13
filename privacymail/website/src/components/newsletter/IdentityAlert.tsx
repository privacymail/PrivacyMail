import React from "react";
import { Trans } from "react-i18next";

const IdentityAlert = () => {
    return (
        <div className="alert warning identityAlert">
            <p>
                <Trans>identity_lowIdentityCount</Trans>
            </p>

            <button>
                <Trans>identity_addIdentity</Trans>
            </button>
        </div>
    );
};
export default IdentityAlert;
