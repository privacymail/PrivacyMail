import React from "react";
import { Trans } from "react-i18next";
import { IconList, IconListItem } from "../../utils/IconList";

const Detection = () => {
    return (
        <div className="detection">
            <h2 className="grid-item regular">
                <Trans>home_howWeDetectIt</Trans>
            </h2>
            <IconList className="image-list grid-item">
                <IconListItem icon={"email"}>
                    <Trans>home_howWeDetectIt1</Trans>
                </IconListItem>
                <IconListItem icon={"search"}>
                    <Trans>home_howWeDetectIt2</Trans>
                </IconListItem>
                <IconListItem icon={"public"}>
                    <Trans>home_howWeDetectIt3</Trans>
                </IconListItem>
                <IconListItem icon={"mood"}>
                    <Trans>home_howWeDetectIt4</Trans>
                </IconListItem>
            </IconList>
        </div>
    );
};
export default Detection;
