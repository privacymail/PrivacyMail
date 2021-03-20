import React, { useState } from "react";
import Collapsible from "react-collapsible";
import { Icon } from "./Icon";

interface CollapsibleItemProps {
    defaultOpen?: boolean; //should the CollapsibleItem be opened by default?
    small?: JSX.Element; //this gets displayed when the CollapsibleItem is collapsed
    big?: JSX.Element | JSX.Element[]; //this gets displayed when the CollapsibleItem is expanded
    children?: JSX.Element[]; //Alternative way to privide small and big. Small should always be the first element in the list.
    className?: string;
}
/**
 * This wraps the Collapsible Class from "react-collapsible" and handles its state.
 *
 */
const CollapsibleItem = (props: CollapsibleItemProps) => {
    const [isExpanded, setIsExpanded] = useState(props.defaultOpen || false);
    return (
        <div className={(props.className ?? "") + " collapsibleItem"}>
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
