import React from "react";
import { Icon } from "../../../utils/Icon";

interface PassOrNotIconProps {
    passed: boolean;
    className?: string;
}
const PassOrNotIcon = (props: PassOrNotIconProps) => {
    return (
        <div className={props.className}>
            <Icon>{props.passed ? "check_circle" : "cancel"}</Icon>
        </div>
    );
};

export default PassOrNotIcon;
