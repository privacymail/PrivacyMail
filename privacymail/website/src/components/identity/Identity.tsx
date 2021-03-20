import React, { useState, useEffect } from "react";
import { Trans } from "react-i18next";
import Stepper, { StepperItem } from "../../utils/Stepper";
import { generateIdentity, IIdentity } from "../../repository/identity";
import Spinner from "../../utils/Spinner";
import Person from "./Person";
import { IconList, IconListItem } from "../../utils/IconList";
import { useParams, Link } from "react-router-dom";
import { isDomainVaild } from "../../utils/functions/isDomainValid";
import InvalidDomain from "../../utils/InvalidDomain";

/**
 * the AddIdentity Process using a Stepper
 */
const Identity = () => {
    const [identity, setIdentity] = useState<IIdentity>();
    const [current, setCurrent] = useState<number>(0);

    const { id } = useParams<any>();

    //resets the scroll, if the urlparams changes
    useEffect(() => window.scrollTo(0, 0), [id]);

    /**
     * Sets the new Identity used in this process.
     * It either sets the idenity or resets the stepper
     * @param ident the new Identity
     */
    const setIdentityCheck = (ident?: IIdentity) => {
        if (ident) {
            setIdentity(ident);
        } else {
            setCurrent(0);
        }
    };
    return (
        <div className="identity">
            <h1>
                <Trans>identity_headline</Trans>
            </h1>
            <Stepper
                content={[
                    {
                        heading: <Trans>identity_start_headline</Trans>,
                        child: <Page1 setIdentity={setIdentityCheck} url={id} />
                    },
                    { heading: <Trans>identity_generate_headline</Trans>, child: <Page2 identity={identity} /> },
                    { heading: <Trans>identity_register_headline</Trans>, child: <Page3 identity={identity} /> },
                    { child: <Page4 identity={identity} /> }
                ]}
                onTabChange={tab => {
                    if (tab === 0) setIdentity(undefined);
                    if (tab) setCurrent(tab);
                }}
                tab={current}
                minHeight={200}
            />
        </div>
    );
};
export default Identity;

interface Page1 extends StepperItem {
    setIdentity: (identity?: IIdentity) => void;
    url?: string;
}
/**
 * Page 1 of the AddIdentity Process
 */
const Page1 = (props: Page1) => {
    /**
     * This generates a new Identity
     */
    const createIdentity = () => {
        generateIdentity(props.url, props.setIdentity);
        props.next?.();
    };
    return isDomainVaild(props.url || "") ? (
        <div className="start">
            <h2>
                <Trans>identity_start_headline</Trans>
            </h2>
            <div>
                <p>
                    <Trans i18nKey="identity_start_explination1">
                        <span className="medium">{{ company: props.url }}</span>
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
        </div>
    ) : (
        <InvalidDomain url={props.url} urlPath={"identity"} />
    );
};
interface Page2 extends StepperItem {
    identity?: IIdentity;
}
/**
 * Page 2 of the AddIdentity Process
 */
const Page2 = (props: Page2) => {
    return (
        <Spinner isSpinning={!props.identity}>
            <h2>
                Your Identity for{" "}
                <a href={"http://" + props.identity?.service.url} target="_blank" rel="noopener noreferrer">
                    {props.identity?.service.url}
                </a>
            </h2>
            <div>
                <Person identity={props.identity} />

                <div className="identityButtons">
                    <button onClick={() => props.jump?.(0)} className="secondary">
                        <Trans>identity_cancel</Trans>
                    </button>
                    <button onClick={() => props.next?.()}>
                        <Trans>identity_next</Trans>
                    </button>
                </div>
            </div>
        </Spinner>
    );
};
interface Page3 extends StepperItem {
    identity?: IIdentity;
}
/**
 * Page 3 of the AddIdentity Process
 */
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
                                </Trans>
                            </p>
                        </IconListItem>
                    </IconList>
                </div>
            </div>
            <div className="identityButtons">
                <button onClick={() => props.jump?.(0)} className="secondary">
                    <Trans>identity_cancel</Trans>
                </button>
                <button onClick={() => props.next?.()}>
                    <Trans>identity_next</Trans>
                </button>
            </div>
        </Spinner>
    );
};
/**
 * Page 4 of the AddIdentity Process
 */
const Page4 = (props: Page2) => {
    return (
        <div className="done">
            <h2>
                <Trans>identity_done_headline</Trans>
            </h2>
            <IconList>
                <IconListItem icon={"check_circle_outline"}>
                    <p className="normal light">
                        <Trans>identity_done_1</Trans>
                    </p>
                </IconListItem>
                <IconListItem icon={"search"}>
                    <p className="normal light">
                        <Trans>identity_done_2</Trans>
                    </p>
                </IconListItem>
                <IconListItem icon={"repeat"}>
                    <p className="normal light">
                        <Trans>identity_done_3</Trans>
                    </p>
                </IconListItem>
                <IconListItem icon={"public"}>
                    <p className="normal light">
                        <Trans i18nKey="identity_done_4">
                            <Link to={"/service/" + props.identity?.service.url}></Link>
                        </Trans>
                    </p>
                </IconListItem>
            </IconList>
            <div className="identityButtons">
                <button onClick={() => props.jump?.(0)}>
                    <Trans>identity_new</Trans>
                </button>
            </div>
        </div>
    );
};
