import React from "react";
import { Trans } from "react-i18next";
import Stepper, { StepperItem } from "../../utils/Stepper";

const Identity = () => {
    return (
        <div>
            <h1>
                <Trans>identity_headline</Trans>
            </h1>
            <h2>
                <Trans>identity_whatToDo</Trans>
            </h2>

            <Stepper
                content={[
                    { heading: <Trans>identity_start_headline</Trans>, child: <Page1 /> },
                    { heading: <Trans>identity_generate_headline</Trans>, child: <Page1 /> },
                    { heading: <Trans>identity_register_headline</Trans>, child: <Page2 /> }
                ]}
            />
        </div>
    );
};
export default Identity;

interface Page1 extends StepperItem {}
const Page1 = (props: Page1) => {
    return (
        <div>
            Hallop<button onClick={() => props.next?.()}>Next</button>
        </div>
    );
};
const Page2 = (props: Page1) => {
    return (
        <div>
            Hallo2<button onClick={() => props.prev?.()}>Prev</button>
        </div>
    );
};
