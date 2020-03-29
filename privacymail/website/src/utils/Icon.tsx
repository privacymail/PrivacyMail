import React from "react";

interface IconPros {
    children: string;
    className?: string;
    onClick?: Function;
}

const Icon = (props: IconPros) => {
    const iconName = props.children;
    if (!iconName) {
        console.error("No icon name provided");
    }

    let image = null;
    try {
        image = require("../assets/images/icons/" + iconName + "-24px.svg");
    } catch (error) {
        try {
            image = require("../assets/images/icons/" + iconName + ".svg");
        } catch (error) {
            try {
                image = require("../assets/images/icons/" + iconName);
            } catch (error) {
                console.error("Can't find image. Please check your spelling");
            }
        }
    }
    return (
        <img
            className={"icon " + (props.className || "")}
            alt={iconName}
            src={image}
            onClick={e => props.onClick?.(e)}
        />
    );
};

export { Icon };
