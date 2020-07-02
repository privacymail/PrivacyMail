import React from "react";
import { IIdentity } from "../../repository/identity";

import { Icon } from "../../utils/Icon";
import { Trans } from "react-i18next";

interface PersonProps {
    identity?: IIdentity;
    className?: string;
}
const Person = (props: PersonProps) => {
    const copyToClipboard = () => {
        navigator.clipboard.writeText(props.identity?.mail || "");
    };

    return (
        <div className={"person" + (props.className ? " " + props.className : "")}>
            <div className={"profilePic " + (props.identity?.gender ? "male" : "female")}>
                <div className="email">
                    <p>{props.identity?.mail}</p>
                    <Icon onClick={copyToClipboard} title={<Trans>copied</Trans>} titleDuration={1000}>
                        file_copy
                    </Icon>
                </div>
            </div>

            <div className="otherInfo">
                <p>
                    <span className="medium">
                        <Trans>identity_name</Trans>
                        {": "}
                    </span>
                    {props.identity?.first_name} {props.identity?.surname}
                </p>
                <p>
                    <span className="medium">
                        <Trans>identity_gender</Trans>
                        {": "}
                    </span>
                    {props.identity?.gender ? <Trans>male</Trans> : <Trans>female</Trans>}
                </p>
                <p>
                    <span className="medium">
                        <Trans>identity_website</Trans>
                        {": "}
                    </span>
                    <a href={"http://" + props.identity?.service.url} target="_blank" rel="noopener noreferrer">
                        {props.identity?.service.url}
                    </a>
                </p>
            </div>
        </div>
    );
};

export default Person;
