import React, { useState } from "react";
import { Icon } from "./Icon";

export interface StepperItem {
    next?: () => void;
    prev?: () => void;
}
interface Stepper {
    content: {
        child: React.ReactElement<StepperItem>;
        heading: string | JSX.Element;
    }[];
}
const Stepper = (props: Stepper) => {
    const [current, setCurrent] = useState<number>(0);
    const currentChild = props.content[current].child;
    return (
        <div className="stepper">
            <StepperHeading headings={props.content.map(elem => elem.heading)} current={current} />
            {React.cloneElement(currentChild, {
                next: current < props.content.length ? () => setCurrent(current + 1) : undefined,
                prev: current > 0 ? () => setCurrent(current - 1) : undefined
            })}
        </div>
    );
};
interface StepperHeading {
    headings: (string | JSX.Element)[];
    current: number;
}
const StepperHeading = (props: StepperHeading) => {
    const getHeadings = (headings: (string | JSX.Element)[]): JSX.Element[] => {
        const arr: JSX.Element[] = [];
        headings.forEach((heading, index) => {
            arr.push(
                <div key={index + "step"} className="step">
                    <span>
                        {props.current <= index ? (
                            <span className={"numberIcon" + (props.current === index ? " active" : " inactive")}>
                                {index + 1}
                            </span>
                        ) : (
                            <Icon>check_circle_fill</Icon>
                        )}
                        <span>{heading}</span>
                    </span>
                </div>
            );
            arr.push(
                <div key={index + "line"} className="line">
                    <span></span>
                </div>
            );
        });
        arr.pop();
        return arr;
    };
    return <div className="heading">{getHeadings(props.headings)}</div>;
};
export default Stepper;
