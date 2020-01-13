import React from "react";

const Icon = props => {
    const iconName = props.children;
    if (!iconName) {
        console.error("No icon name provided");
    }
    console.log(iconName);

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
    return <object className={"icon " + (props.className || "")} type="image/svg+xml" data={image} alt="iconName" />;
};

export { Icon };
