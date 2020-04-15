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
        <div className="analysisItem">
            <Collapsible
                onOpening={() => setIsExpanded(true)}
                onClosing={() => setIsExpanded(false)}
                open={props.defaultOpen}
                trigger={
                    <div className="analysisSmall">
                        {props.children?.[0] || props.small}
                        <div className="expandable">
                            <Icon className={isExpanded ? " expanded" : " closed"}>expand</Icon>
                        </div>
                    </div>
                }
            >
                {props.children?.filter((e, index) => index !== 0) || props.big}
            </Collapsible>
        </div>
    );
};

export default CollapsibleItem;
