import React from "react";
import { getRatingColor } from "../../../utils/getRatingColor";

interface ColoredNumbers {
    number?: number;
    className?: string;
}
const ColoredNumbers = (props: ColoredNumbers) => {
    const numberToFraction = (number: number) => {
        return -Math.pow(0.5, number) + 1;
    };
    return (
        <div
            className={props.className || "coloredNumber"}
            style={{ color: getRatingColor(numberToFraction(props.number || 0)) }}
        >
            {props.number}
        </div>
    );
};
export default ColoredNumbers;
