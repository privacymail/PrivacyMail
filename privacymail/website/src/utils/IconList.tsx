import React from "react";
import { Icon } from "./Icon";

interface IconListProps {
    className?: string;
    children?: JSX.Element | JSX.Element[];
}
/**
 * Generates an IconList as seen on the Homepage
 */
const IconList = (props: IconListProps) => {
    return (
        <div className={props.className || "image-list"}>
            <ul>{props.children}</ul>
        </div>
    );
};

interface IconListItemProps {
    icon?: string;
    children?: JSX.Element | JSX.Element[];
}
/**
 * Generates an IconListItem for the IconList
 */
const IconListItem = (props: IconListItemProps) => {
    return (
        <li>
            <Icon>{props.icon || ""}</Icon>
            <div className="iconListContent">{props.children}</div>
        </li>
    );
};

export { IconList, IconListItem };
