import React, { useState } from "react";
import { Trans } from "react-i18next";
import Stepper, { StepperItem } from "../../utils/Stepper";
import { generateIdentity, IIdentity } from "../../repository/identity";
import Spinner from "../../utils/Spinner";
import Person from "./Person";
import { IconList, IconListItem } from "../../utils/IconList";

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
                minHeight={400}
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
                <a href={"http://" + props.identity?.service.url} target="_blank" rel="noopener noreferrer">
                    {props.identity?.service.url}
                </a>
            </h2>
            <Person identity={props.identity} />

            <div className="identityButtons">
                <button onClick={() => props.prev?.()} className="secondary">
                    <Trans>cancel</Trans>
                </button>
                <button onClick={() => props.next?.()}>
                    <Trans>next</Trans>
                </button>
            </div>
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
            <div className="instructions">
                <Person identity={props.identity} className="smallView" />
                <div className="steps">
                    <IconList>
                        <IconListItem icon={"file_copy"}>
                            <p className="normal light">
                                <Trans>identity_instruction_step1</Trans>
                            </p>
                        </IconListItem>
                        <IconListItem icon={"how_to_reg"}>
                            <p className="normal light">
                                <Trans i18nKey="identity_instruction_step2">
                                    <a
                                        href={"http://" + props.identity?.service.url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                    >
                                        {{ company: props.identity?.service.url }}
                                    </a>
                                </Trans>
                            </p>
                        </IconListItem>
                    </IconList>
                    <IconList>
                        <IconListItem icon={"warning"}>
                            <p className="normal light">
                                <Trans i18nKey="identity_instruction_warning">
                                    <span className="regular"></span>
                                    <span className="regular">
                                        <a
                                            href={"http://" + props.identity?.service.url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                        >
                                            {{ company: props.identity?.service.url }}
                                        </a>
                                    </span>
                                    }}
                                </Trans>
                            </p>
                        </IconListItem>
                    </IconList>
                </div>
            </div>
            <div className="identityButtons">
                <button onClick={() => props.prev?.()} className="secondary">
                    <Trans>cancel</Trans>
                </button>
                <button onClick={() => props.next?.()}>
                    <Trans>next</Trans>
                </button>
            </div>
        </Spinner>
    );
};
