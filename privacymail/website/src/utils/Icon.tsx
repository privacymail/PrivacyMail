import React from "react";
import { addTooltip, removeTooltip } from "./Tooltip";

interface IconPros {
    children: string; //the name of the icon
    className?: string; //an additional classname to be applied to the icon
    onClick?: Function; //an optinal onClick function for the icon
    title?: string | JSX.Element; //This will get displayed as an onHover (on Desktop) or onClick (on Mobile) tooltip
    titleDuration?: number; //if provided the tooltip will close automaticly after x milliseconds
    height?: number; //the height of the icon
    id?: string; //an additional id to be applied to the icon
    importByFile?: boolean; //Does not import the icon via the iconfont but imports the icon as a file from the icon folder
}
interface IconState {
    tooltip: number;
}
class Icon extends React.Component<IconPros, IconState> {
    //this tracks how many tooltips are opened by this icon
    tooltip = -1;

    /**
     * Handels the onClickEvent of the Icon.
     * This opens the Tooltips for the Icon.
     *
     * @param e the onClickEvent of the Icon
     */
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
    /**
     * Opens the Tooltips and manages the tooltip variable
     * @param target The Icon where the tooltip should be displayed
     */
    openTooltip(target: HTMLElement) {
        if (this.tooltip < 0) {
            this.tooltip = addTooltip(this.props.title, target, () => (this.tooltip = -1));
            //this.tooltip = addTooltip(this.props.title, target, () => console.log("got closed"));
        }
    }
    /**
     * Closes the Tooltips and manages the tooltip variable+
     */
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

        //if the flag is set, this searches for the icon
        if (this.props.importByFile) {
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
        }
        //The IconFont doesnt work with the icon tag. Therefore a span option is also implemented
        return (
            <div className={"icon " + (this.props.className || "")}>
                {}
                {this.props.importByFile ? (
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
                ) : (
                    <span
                        className={"icon-" + iconName}
                        style={{ fontSize: this.props.height }}
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
                )}
            </div>
        );
    }
}

export { Icon };
