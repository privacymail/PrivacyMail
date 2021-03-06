import React, { useState, useRef, useEffect } from "react";
import { Icon } from "./Icon";

export interface StepperItem {
    next?: () => void; //this calls the next step
    prev?: () => void; // this calls to the previous step
    jump?: (tab: number) => void; //this jumps to a specific step
}
interface Stepper {
    content: {
        //all the steps
        child: React.ReactElement<StepperItem>; //the underlying content of the step
        heading?: string | JSX.Element; //headline of the step
    }[];
    onTabChange?: (step?: number) => void; //this will get called if the current Step changes
    minHeight?: number; //this is the minHeigt of the Stepper
    tab?: number; //the initial tab where the Stepper should start.
}
/**
 * This is the Logic behind the Stepper used to add a new Identity
 */
const Stepper = (props: Stepper) => {
    const [current, setCurrent] = useState<number>(0);
    const currentChild = props.content[current].child;

    const stepperRef = useRef<any>(null);

    const setTab = (tab: number) => {
        setCurrent(tab);
        props.onTabChange?.(tab);
    };
    //this resets the view after each step
    useEffect(() => {
        if (current !== 0) {
            stepperRef?.current?.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });
        }
    }, [current]);
    useEffect(() => {
        if (props.tab !== current) {
            setCurrent(props.tab ?? current);
        }
        // eslint-disable-next-line
    }, [props.tab]);

    //renders all the steps and provides them with the needed functions for a StepperItem
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
/**
 * This acts as a progress bar.
 * So the user knows at which step he/she is
 */
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
                                <Icon height={24}>check_circle_fill</Icon>
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
