import React, { useState, useEffect } from "react";
import { Trans } from "react-i18next";
import Stepper, { StepperItem } from "../../utils/Stepper";
import { generateIdentity, IIdentity } from "../../repository/identity";
import Spinner from "../../utils/Spinner";
import Person from "./Person";
import { IconList, IconListItem } from "../../utils/IconList";
import { useParams, Link } from "react-router-dom";

const Identity = () => {
    const [identity, setIdentity] = useState<IIdentity>();
    const { id } = useParams();
    useEffect(() => window.scrollTo(0, 0), [id]);
    return (
        <div className="identity">
            <h1>
                <Trans>identity_headline</Trans>
            </h1>
            <Stepper
                content={[
                    {
                        heading: <Trans>identity_start_headline</Trans>,
                        child: <Page1 setIdentity={setIdentity} url={id} />
                    },
                    { heading: <Trans>identity_generate_headline</Trans>, child: <Page2 identity={identity} /> },
                    { heading: <Trans>identity_register_headline</Trans>, child: <Page3 identity={identity} /> },
                    { child: <Page4 /> }
                ]}
                onTabChange={tab => {
                    if (tab === 0) setIdentity(undefined);
                }}
                minHeight={200}
            />
        </div>
    );
};
export default Identity;

interface Page1 extends StepperItem {
    setIdentity: (identity: IIdentity) => void;
    url?: string;
}
const Page1 = (props: Page1) => {
    const [url, setUrl] = useState<string>(props.url || "");

    useEffect(() => {
        if (props.url) setUrl(props.url);
    }, [props.url]);
    const createIdentity = () => {
        generateIdentity(props.url, props.setIdentity);
        props.next?.();
    };

    //according to https://stackoverflow.com/a/26987741/9851505 this is a regex for valid domains
    const validDomainRegex = new RegExp(
        "^(((?!-))(xn--|_{1,1})?[a-z0-9-]{0,61}[a-z0-9]{1,1}.)*(xn--)?([a-z0-9][a-z0-9-]{0,60}|[a-z0-9-]{1,30}.[a-z]{2,})$"
    );
    return validDomainRegex.test(props.url || "") ? (
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
        <div className="invalid">
            <h2>
                <Trans>identity_invalid_domain</Trans>
            </h2>
            <div>
                <p>
                    <Trans i18nKey="identity_invalid_text">
                        <span className="medium">{{ domain: props.url }}</span>
                    </Trans>
                </p>
                <div>
                    <input value={url} onChange={e => setUrl(e.target.value)} />
                    <Link to={"/identity/" + url}>
                        <button id="analizeButton">
                            <Trans>404_button</Trans>
                        </button>
                    </Link>
                </div>
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
                <button onClick={() => props.jump?.(0)} className="secondary">
                    <Trans>cancel</Trans>
                </button>
                <button onClick={() => props.next?.()}>
                    <Trans>next</Trans>
                </button>
            </div>
        </Spinner>
    );
};

const Page4 = (props: StepperItem) => {
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
                        <Trans>identity_done_4</Trans>
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
