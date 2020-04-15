import React from "react";

interface ColoredNumbers {
    number?: number;
    className?: string;
}
const ColoredNumbers = (props: ColoredNumbers) => {
    return (
        <div className={props.className || "coloredNumber"} style={{ color: "#f57c00" }}>
            {props.number}
        </div>
    );
};
export default ColoredNumbers;
