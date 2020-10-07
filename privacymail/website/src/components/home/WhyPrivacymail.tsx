import React from "react";
import { Trans } from "react-i18next";
import { IconList, IconListItem } from "../../utils/IconList";

/**
 * This explaines why somebody should use PrivacyMail
 */
const WhyPrivacymail = () => {
    return (
        <div className="whyPrivacymail">
            <h2 className="grid-item regular">
                <Trans>home_whyUsePM</Trans>
            </h2>
            <IconList className="image-list grid-item">
                <IconListItem icon={"email"}>
                    <h3>
                        <Trans>home_whyUsePM1</Trans>
                    </h3>
                    <p className="normal light">
                        <Trans>home_whyUsePM1detail</Trans>
                    </p>
                </IconListItem>
                <IconListItem icon={"record_voice_over"}>
                    <h3>
                        <Trans>home_whyUsePM2</Trans>
                    </h3>
                    <p className="normal light">
                        <Trans>home_whyUsePM2detail</Trans>
                    </p>
                </IconListItem>
                <IconListItem icon={"school"}>
                    <h3>
                        <Trans>home_whyUsePM3</Trans>
                    </h3>
                    <p className="normal light">
                        <Trans>home_whyUsePM3detail</Trans>
                    </p>
                </IconListItem>
            </IconList>
        </div>
    );
};
export default WhyPrivacymail;
