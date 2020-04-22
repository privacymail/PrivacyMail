import React from "react";
import { Trans } from "react-i18next";
import Stepper, { StepperItem } from "../../utils/Stepper";

const Identity = () => {
    return (
        <div className="identity">
            <h1>
                <Trans>identity_headline</Trans>
            </h1>
            <Stepper
                content={[
                    { heading: <Trans>identity_start_headline</Trans>, child: <Page1 /> },
                    { heading: <Trans>identity_generate_headline</Trans>, child: <Page1 /> },
                    { child: <Page1 /> },
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
        <div className="start">
            <p>
                <Trans i18nKey="identity_start_explination">
                    <span className="medium">{{ company: "3m.com" }}</span>
                </Trans>
            </p>

            <div>
                <button onClick={() => props.next?.()}>
                    <Trans>identity_start_generateButton</Trans>
                </button>
            </div>
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
