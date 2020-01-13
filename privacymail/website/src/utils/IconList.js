import React from "react";
import { Icon } from "./Icon";

const IconList = props => {
    return (
        <div className={props.className || ""}>
            <ul>{props.children}</ul>
        </div>
    );
};
const IconListItem = props => {
    return (
        <li>
            <Icon>{props.icon}</Icon>
            <span>{props.children}</span>
        </li>
    );
};

export { IconList, IconListItem };
