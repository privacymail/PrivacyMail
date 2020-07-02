import React, { useState } from "react";
import Collapsible from "react-collapsible";
import { Icon } from "./Icon";

interface CollapsibleItemProps {
    defaultOpen?: boolean;
    small?: JSX.Element;
    big?: JSX.Element | JSX.Element[];
    children?: JSX.Element[];
}
const CollapsibleItem = (props: CollapsibleItemProps) => {
    const [isExpanded, setIsExpanded] = useState(props.defaultOpen || false);
    return (
        <div className="collapsibleItem">
            <Collapsible
                onOpening={() => setIsExpanded(true)}
                onClosing={() => setIsExpanded(false)}
                open={props.defaultOpen}
                trigger={
                    <div className="collapsibleSmall">
                        {props.children?.[0] || props.small}
                        <div className="expandable">
                            <Icon className={isExpanded ? " expanded" : " closed"}>expand</Icon>
                        </div>
                    </div>
                }
            >
                <div className="collapsibleBig">{props.children?.filter((e, index) => index !== 0) || props.big}</div>
            </Collapsible>
        </div>
    );
};

export default CollapsibleItem;
