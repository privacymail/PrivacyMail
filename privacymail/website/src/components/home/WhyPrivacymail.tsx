import React from "react";
import { Trans } from "react-i18next";
import { IconList, IconListItem } from "../../utils/IconList";

const WhyPrivacymail = () => {
    return (
        <div className="whyPrivacymail">
            <h2 className="grid-item regular">
                <Trans>home_whyUsePM</Trans>
            </h2>
            <IconList className="image-list grid-item">
                <IconListItem icon={"email"}>
                    <p className="medium big">
                        <Trans>home_whyUsePM1</Trans>
                    </p>
                    <p className="normal light">
                        <Trans>home_whyUsePM1detail</Trans>
                    </p>
                </IconListItem>
                <IconListItem icon={"record_voice_over"}>
                    <p className="medium big">
                        <Trans>home_whyUsePM2</Trans>
                    </p>
                    <p className="normal light">
                        <Trans>home_whyUsePM2detail</Trans>
                    </p>
                </IconListItem>
                <IconListItem icon={"school"}>
                    <p className="medium big">
                        <Trans>home_whyUsePM3</Trans>
                    </p>
                    <p className="normal light">
                        <Trans>home_whyUsePM3detail</Trans>
                    </p>
                </IconListItem>
            </IconList>
        </div>
    );
};
export default WhyPrivacymail;
