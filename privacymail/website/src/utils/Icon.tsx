import React, { useState } from "react";
import { ReactSVG } from "react-svg";

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
    let imageUrl = null;
    let type = "svg";
    try {
        image = require("../assets/images/icons/" + iconName + "-24px.svg");
        imageUrl = "../assets/images/icons/" + iconName + "-24px.svg";
        type = "svg";
    } catch (error) {
        try {
            image = require("../assets/images/icons/" + iconName + ".svg");
            imageUrl = "../assets/images/icons/" + iconName + ".svg";
            type = "svg";
        } catch (error) {
            try {
                image = require("../assets/images/icons/" + iconName);
                imageUrl = "../assets/images/icons/" + iconName;
                type = iconName.split(".").pop() ?? "";
            } catch (error) {
                try {
                    image = require("../assets/images/icons/" + iconName + ".png");
                    imageUrl = "../assets/images/icons/" + iconName + ".png";
                    type = "png";
                } catch (error) {
                    console.error("Can't find image: '" + iconName + "' . Please check your spelling");
                }
            }
        }
    }

    const onClick = (e: React.MouseEvent) => {
        console.log("clicks");

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
        <div className={"icon " + (props.className || "")} style={{ height: props.height }}>
            {type === "svg" && imageUrl ? (
                <ReactSVG
                    src={image}
                    onClick={onClick}
                    beforeInjection={svg => {
                        console.log("svg", svg.getAttribute("height"), svg.getAttribute("width"));
                        const height = svg.getAttribute("height");
                        const width = svg.getAttribute("width");
                        if (props.height && height && width) {
                            const aspectRatio = props.height / parseFloat(height);
                            svg.setAttribute("transform", "scale(" + aspectRatio + ")");
                            svg.setAttribute("height", String(parseFloat(height) * aspectRatio));
                            svg.setAttribute("width", String(parseFloat(width) * aspectRatio));

                            console.log("svg", svg.children.item);
                        }
                    }}
                    onMouseOver={() => setTooltipOpen(true)}
                    onMouseOut={() => setTooltipOpen(false)}
                    id={props.id}
                />
            ) : (
                <img
                    alt={iconName}
                    height={props.height}
                    src={image}
                    onClick={e => onClick(e)}
                    onMouseOver={() => setTooltipOpen(true)}
                    onMouseOut={() => setTooltipOpen(false)}
                    id={props.id}
                />
            )}

            {props.title && isTooltipOpen && <div className="tooltip">{props.title}</div>}
        </div>
    );
};

export { Icon };
