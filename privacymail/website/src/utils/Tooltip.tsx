import React, { useEffect, useState } from "react";

interface Tooltip {
    id: number;
    position: {
        x: number;
        y: number;
    };
    content?: JSX.Element | JSX.Element[] | string;
}

let tooltipIdCounter = 1;

export const addTooltip = (content: JSX.Element | JSX.Element[] | string | undefined, element: HTMLElement): number => {
    const rect = element.getBoundingClientRect();
    return addTooltipByCord(content, rect.left, rect.top);
};
export const addTooltipByCord = (
    content: JSX.Element | JSX.Element[] | string | undefined,
    x: number,
    y: number
): number => {
    tooltipIdCounter++;
    const event = new CustomEvent<Tooltip>("openTooltip", {
        detail: {
            id: tooltipIdCounter,
            position: {
                x: x,
                y: y
            },
            content
        }
    });
    console.log({
        detail: {
            id: tooltipIdCounter,
            position: {
                x: x,
                y: y
            },
            content
        }
    });

    document.dispatchEvent(event);
    return tooltipIdCounter;
};

export const removeTooltip = (id: number) => {
    console.log("closed: ", id);

    const event = new CustomEvent<number>("closeTooltip", {
        detail: id
    });
    document.dispatchEvent(event);
};

const Tooltip = () => {
    const [tooltips, setTooltips] = useState<Tooltip[]>([]);

    useEffect(() => {
        const addTooltip = (e: CustomEvent<Tooltip>) => {
            setTooltips(old => [...old, e.detail]);
        };
        const closeTooltip = (e: CustomEvent<number>) => {
            setTooltips(old => {
                const index = old.findIndex(tooltip => tooltip.id === e.detail);
                if (index >= 0) {
                    old.splice(index, 1);
                }
                return [...old];
            });
        };

        document.addEventListener("openTooltip", addTooltip as EventListener);
        document.addEventListener("closeTooltip", closeTooltip as EventListener);

        return () => {
            document.removeEventListener("openTooltip", addTooltip as EventListener);
            document.removeEventListener("closeTooltip", closeTooltip as EventListener);
        };
    }, []);

    return (
        <div className="tooltips">
            {tooltips.map((tooltip, index) => (
                <div className="tooltip" key={index} style={{ top: tooltip.position.y, left: tooltip.position.x }}>
                    {tooltip.content}
                </div>
            ))}
        </div>
    );
};

export default Tooltip;
