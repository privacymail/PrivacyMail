import React from "react";
import { getRatingColor } from "../../../utils/functions/getRatingColor";

interface ColoredNumbers {
    number?: number; //number of violations found
    className?: string;
    pow?: number; //decides how fast the conversion should reach 1
}
/**
 * Colores a Number based on the number of violations
 */
const ColoredNumbers = (props: ColoredNumbers) => {
    /**
     * Converts any number to a number between 0 and 1
     * @param number The number of violations
     */
    const numberToFraction = (number: number) => {
        return -Math.pow(1 - (props.pow ?? 0.5), number) + 1;
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
