import React from "react";
import { addTooltip, removeTooltip } from "./Tooltip";

interface IconPros {
    children: string;
    className?: string;
    onClick?: Function;
    title?: string | JSX.Element;
    titleDuration?: number;
    height?: number;
    id?: string;
}
interface IconState {
    tooltip: number;
}
class Icon extends React.Component<IconPros, IconState> {
    tooltip = -1;

    onClick(e: React.MouseEvent) {
        this.props.onClick?.(e);
        if (this.props.title) {
            if (this.tooltip < 0) {
                if (this.props.titleDuration) {
                    window.setTimeout(() => this.closeTooltip(), this.props.titleDuration);
                }

                this.openTooltip(e.target as HTMLElement);
            }
        }
    }
    openTooltip(target: HTMLElement) {
        if (this.tooltip < 0) {
            this.tooltip = addTooltip(this.props.title, target, () => (this.tooltip = -1));
            //this.tooltip = addTooltip(this.props.title, target, () => console.log("got closed"));
        }
    }
    closeTooltip() {
        if (this.tooltip > 0) {
            removeTooltip(this.tooltip);
            this.tooltip = -1;
        }
    }
    render() {
        const iconName = this.props.children;
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
                        console.error("Can't find image: '" + iconName + "' . Please check your spelling");
                    }
                }
            }
        }

        return (
            <div className={"icon " + (this.props.className || "")}>
                <img
                    alt={iconName}
                    height={this.props.height}
                    src={image}
                    onClick={e => this.onClick(e)}
                    onMouseEnter={e =>
                        !this.props.titleDuration && this.props.title && this.openTooltip(e.target as HTMLElement)
                    }
                    onMouseLeave={() => {
                        if (!this.props.titleDuration && this.props.title) {
                            this.closeTooltip();
                        }
                    }}
                    id={this.props.id}
                />
            </div>
        );
    }
}

export { Icon };
