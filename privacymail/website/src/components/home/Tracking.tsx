import React from "react";
import { Trans } from "react-i18next";
import { IconList, IconListItem } from "../../utils/IconList";

/**
 * This explaines how tracking works
 */
const Tracking = () => {
    return (
        <div className="tracking">
            <h2 className="grid-item regular">
                <Trans>home_howItWorks</Trans>
            </h2>
            <IconList className="image-list grid-item">
                <IconListItem icon={"email"}>
                    <Trans>home_howItWorks1</Trans>
                </IconListItem>
                <IconListItem icon={"done_all"}>
                    <Trans>home_howItWorks2</Trans>
                </IconListItem>
                <IconListItem icon={"insert_link"}>
                    <Trans>home_howItWorks3</Trans>
                </IconListItem>
                <IconListItem icon={"attach_money"}>
                    <Trans>home_howItWorks4</Trans>
                </IconListItem>
            </IconList>
        </div>
    );
};
export default Tracking;
