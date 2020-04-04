import React, { useState } from "react";

interface IconPros {
    children: string;
    className?: string;
    onClick?: Function;
    title?: string | JSX.Element;
    height?: number;
    id?: string;
}

const Icon = (props: IconPros) => {
    const [isTooltipOpen, setTooltipOpen] = useState(false);

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
                try {
                    image = require("../assets/images/icons/" + iconName + ".png");
                } catch (error) {
                    console.error("Can't find image. Please check your spelling");
                }
            }
        }
    }

    const onClick = (e: React.MouseEvent) => {
        props.onClick?.(e);
        if (props.title) {
            if (!isTooltipOpen) {
                const disable = () => {
                    setTooltipOpen(false);
                    document.removeEventListener("click", disable);
                };
                document.addEventListener("click", disable);
                setTooltipOpen(true);
            }
        }
    };

    return (
        <div className={"icon " + (props.className || "")}>
            <img
                alt={iconName}
                height={props.height}
                src={image}
                onClick={e => onClick(e)}
                onMouseOver={() => setTooltipOpen(true)}
                onMouseOut={() => setTooltipOpen(false)}
                id={props.id}
            />
            {props.title && isTooltipOpen && <div className="tooltip">{props.title}</div>}
        </div>
    );
};

export { Icon };
