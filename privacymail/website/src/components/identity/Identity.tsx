import React, { useState } from "react";
import { Trans } from "react-i18next";
import Stepper, { StepperItem } from "../../utils/Stepper";
import { generateIdentity, IIdentity } from "../../repository/identity";
import Spinner from "../../utils/Spinner";
import Person from "./Person";

const Identity = () => {
    const [identity, setIdentity] = useState<IIdentity>();
    return (
        <div className="identity">
            <h1>
                <Trans>identity_headline</Trans>
            </h1>
            <Stepper
                content={[
                    { heading: <Trans>identity_start_headline</Trans>, child: <Page1 setIdentity={setIdentity} /> },
                    { heading: <Trans>identity_generate_headline</Trans>, child: <Page2 identity={identity} /> },
                    { heading: <Trans>identity_register_headline</Trans>, child: <Page3 identity={identity} /> }
                ]}
                onTabChange={tab => {
                    if (tab === 0) setIdentity(undefined);
                }}
            />
        </div>
    );
};
export default Identity;

interface Page1 extends StepperItem {
    setIdentity: (identity: IIdentity) => void;
}
const Page1 = (props: Page1) => {
    const createIdentity = () => {
        generateIdentity("3m.com", props.setIdentity);
        props.next?.();
    };

    return (
        <div className="start">
            <h2>
                <Trans>identity_start_headline</Trans>
            </h2>
            <p>
                <Trans i18nKey="identity_start_explination1">
                    <span className="medium">{{ company: "3m.com" }}</span>
                </Trans>
            </p>
            <p className="regular">
                <Trans>identity_start_explination2</Trans>
            </p>

            <div>
                <button onClick={createIdentity}>
                    <Trans>identity_start_generateButton</Trans>
                </button>
            </div>
        </div>
    );
};
interface Page2 extends StepperItem {
    identity?: IIdentity;
}
const Page2 = (props: Page2) => {
    return (
        <Spinner isSpinning={!props.identity}>
            <h2>
                Your Identity for{" "}
                <a href="http://nytimes.com" target="_blank" rel="noopener noreferrer">
                    nytimes.com
                </a>
            </h2>
            <Person identity={props.identity} />
            <button onClick={() => props.prev?.()}>Prev</button>
            <button onClick={() => props.next?.()}>next</button>
        </Spinner>
    );
};
interface Page3 extends StepperItem {
    identity?: IIdentity;
}
const Page3 = (props: Page3) => {
    return (
        <Spinner isSpinning={!props.identity}>
            <h2>Register your Identity </h2>
            <Person identity={props.identity} />
            <button onClick={() => props.prev?.()}>Prev</button>
            <button onClick={() => props.next?.()}>next</button>
        </Spinner>
    );
};
