import React, { useEffect } from "react";

interface SpinnerProps {
    isSpinning: boolean;
    children: any;
}
/**
 * Creates a Spinner to give the User Feedback that the website is doing something
 */
const Spinner = (props: SpinnerProps) => {
    useEffect(() => window.scrollTo(0, 0), [props.isSpinning]);

    return props.isSpinning ? (
        <div className="spinner">
            <div />
        </div>
    ) : (
        props.children
    );
};

export default Spinner;
