import React from "react";
import { IIdentity } from "../../repository/identity";

import male from "../../assets/images/male.jpg";
import female from "../../assets/images/female.jpg";
import { Icon } from "../../utils/Icon";

interface PersonProps {
    identity?: IIdentity;
}
const Person = (props: PersonProps) => {
    const copyToClipboard = () => {
        navigator.clipboard.writeText(props.identity?.mail || "");
    };

    return (
        <div className="person">
            <img
                className="picture"
                src={props.identity?.gender ? male : female}
                alt={props.identity?.gender ? "male" : "female"}
            />
            <div className="email">
                <p>{props.identity?.mail}</p>
                <Icon onClick={copyToClipboard}>file_copy</Icon>
            </div>
        </div>
    );
};

export default Person;
