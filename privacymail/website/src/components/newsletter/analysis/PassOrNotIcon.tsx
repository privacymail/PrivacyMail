import React from "react";
import { Icon } from "../../../utils/Icon";

interface PassOrNotIconProps {
    status?: PassOrNotState;
    className?: string;
}

export enum PassOrNotState {
    Denied = "Denied",
    Passed = "Passed",
    Disabled = "Disabled"
}

const PassOrNotIcon = (props: PassOrNotIconProps) => {
    const getIcon = (status: PassOrNotState | undefined) => {
        switch (status) {
            case PassOrNotState.Denied:
                return <Icon>cancel</Icon>;
            case PassOrNotState.Passed:
                return <Icon>check_circle</Icon>;
            case PassOrNotState.Disabled:
                return <Icon>remove_circle</Icon>;
            default:
                return null;
        }
    };
    return <div className={props.className}>{getIcon(props.status)}</div>;
};

export default PassOrNotIcon;
