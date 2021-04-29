import React, { useEffect, useState } from "react";

interface TooltipOptions {
    onClose?: () => void;
    timeout?: number;
    className?: string;
}

interface Tooltip {
    id: number;
    position: {
        x: number;
        y: number;
    };
    content?: JSX.Element | JSX.Element[] | string;
    options?: TooltipOptions;
}
//This is a counter to count the displayed tooltips. With this no tooltip id should be assigned twice
let tooltipIdCounter = 1;

/**
 * This function will be used by other Components to generate a tooltip
 * @param content This will be displayed by the tooltip
 * @param element This is the element where the tooltip will be displayed
 * @param onClose This will be called as soon as the tooltip got closed
 * @returns The ID of the generated tooltip
 */
export const addTooltip = (
    content: JSX.Element | JSX.Element[] | string | undefined,
    element: HTMLElement,
    options?: TooltipOptions
): number => {
    const rect = element.getBoundingClientRect();
    return addTooltipByCord(content, rect.left, rect.top + 30, options);
};

/**
 * This function will be used by other Components to generate a tooltip
 * @param content This will be displayed by the tooltip
 * @param x This is the x coordinate where the tooltip will be displayed
 * @param y This is the y coordinate where the tooltip will be displayed
 * @param onClose This will be called as soon as the tooltip got closed
 * @returns The ID of the generated tooltip
 */
export const addTooltipByCord = (
    content: JSX.Element | JSX.Element[] | string | undefined,
    x: number,
    y: number,
    options?: TooltipOptions
): number => {
    tooltipIdCounter++;
    const event = new CustomEvent<Tooltip>("openTooltip", {
        detail: {
            id: tooltipIdCounter,
            position: {
                x: x,
                y: y
            },
            content,
            options
        }
    });
    document.dispatchEvent(event);

    if (options?.timeout) {
        window.setTimeout(() => {
            removeTooltip(tooltipIdCounter);
        }, options.timeout);
    }
    return tooltipIdCounter;
};
/**
 * This function will close the tooltip with the given id
 * @param id The Id of the tooltip
 */
export const removeTooltip = (id: number) => {
    const event = new CustomEvent<number>("closeTooltip", {
        detail: id
    });
    document.dispatchEvent(event);
};

/**
 * This manages all Tooltips
 */
const Tooltip = () => {
    //Array with all the currently displayed Tooltips
    const [tooltips, setTooltips] = useState<Tooltip[]>([]);

    useEffect(() => {
        /**
         * Adds a Tooltip to all the other tooltips
         * @param e The Custom Tooltip Event
         */
        const addTooltip = (e: CustomEvent<Tooltip>) => {
            setTooltips(old => [...old, e.detail]);
        };
        /**
         * Removes a Tooltip to all the other tooltips
         * @param e The Custom Event with the Id of the tooltip that should be closed
         */
        const closeTooltip = (e: CustomEvent<number>) => {
            setTooltips(old => {
                const index = old.findIndex(tooltip => tooltip.id === e.detail);
                if (index >= 0) {
                    old[index]?.options?.onClose?.();
                    old.splice(index, 1);
                }
                return [...old];
            });
        };
        /**
         * This closes all Tooltips.
         * Note: This will be triggered as soon as the content on the pages moves, because otherwise the position of the tooltip would be wrong
         */
        const closeAll = () => {
            if (tooltips.length >= 1) {
                tooltips.forEach(tooltip => tooltip.options?.onClose?.());

                setTooltips([]);
            }
        };

        //This adds the neccesary EventListeners
        document.addEventListener("openTooltip", addTooltip as EventListener);
        document.addEventListener("closeTooltip", closeTooltip as EventListener);
        window.addEventListener("touchstart", closeAll);

        //This cleans up the EventListeners after the component is unmounted
        return () => {
            document.removeEventListener("openTooltip", addTooltip as EventListener);
            document.removeEventListener("closeTooltip", closeTooltip as EventListener);
            window.removeEventListener("touchstart", closeAll);
        };
    });

    // Generates all tooltips
    return (
        <div className="tooltips">
            {tooltips.map((tooltip, index) => (
                <div
                    className={tooltip.options?.className ?? "tooltip"}
                    key={index}
                    style={{ top: tooltip.position.y, left: tooltip.position.x, position: "fixed", zIndex: 9999 }}
                >
                    {tooltip.content}
                </div>
            ))}
        </div>
    );
};

export default Tooltip;
