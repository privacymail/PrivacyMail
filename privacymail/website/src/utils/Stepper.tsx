import React, { useState, useRef, useEffect } from "react";
import { Icon } from "./Icon";

export interface StepperItem {
    next?: () => void;
    prev?: () => void;
    jump?: (tab: number) => void;
}
interface Stepper {
    content: {
        child: React.ReactElement<StepperItem>;
        heading?: string | JSX.Element;
    }[];
    onTabChange?: (step?: number) => void;
    minHeight?: number;
}
const Stepper = (props: Stepper) => {
    const [current, setCurrent] = useState<number>(0);
    const currentChild = props.content[current].child;

    const stepperRef = useRef<any>(null);

    const setTab = (tab: number) => {
        setCurrent(tab);
        props.onTabChange?.(tab);
    };
    useEffect(() => {
        if (current !== 0) {
            stepperRef?.current?.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });
        }
    }, [current]);
    return (
        <div className="stepper">
            <StepperHeading headings={props.content.map(elem => elem.heading)} current={current} />
            <div className="stepperContent" style={{ minHeight: props.minHeight }} ref={stepperRef}>
                {React.cloneElement(currentChild, {
                    next: current + 1 < props.content.length ? () => setTab(current + 1) : undefined,
                    prev: current > 0 ? () => setTab(current - 1) : undefined,
                    jump: (index: number) => {
                        if (index + 1 < props.content.length && index >= 0) setTab(index);
                    }
                })}
            </div>
        </div>
    );
};
interface StepperHeading {
    headings: (string | JSX.Element | undefined)[];
    current: number;
}
const StepperHeading = (props: StepperHeading) => {
    const getHeadings = (headings: (string | JSX.Element | undefined)[]): JSX.Element[] => {
        const arr: JSX.Element[] = [];
        let lastIndex = 0;
        headings.forEach((heading, index) => {
            if (heading) {
                lastIndex++;
                arr.push(
                    <div key={index + "step"} className="step">
                        <span>
                            {props.current <= index ? (
                                <span className={"numberIcon" + (props.current === index ? " active" : " inactive")}>
                                    {lastIndex}
                                </span>
                            ) : (
                                <Icon>check_circle_fill</Icon>
                            )}
                            {heading}
                        </span>
                    </div>
                );
                arr.push(
                    <div key={index + "line"} className="line">
                        <span></span>
                    </div>
                );
            }
        });
        arr.pop();
        return arr;
    };
    return <div className="heading">{getHeadings(props.headings)}</div>;
};
export default Stepper;
