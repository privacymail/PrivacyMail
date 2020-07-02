import React from "react";
import { getRatingColor } from "../../../utils/functions/getRatingColor";

interface ColoredNumbers {
    number?: number;
    className?: string;
    pow?: number;
}
const ColoredNumbers = (props: ColoredNumbers) => {
    const numberToFraction = (number: number) => {
        return -Math.pow(1 - (props.pow ?? 0.5), number) + 1;
    };
    console.log(props.pow, numberToFraction(props.number || 0));

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
