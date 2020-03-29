import React, { useState } from "react";
import { Trans } from "react-i18next";
import { IThirdParty } from "../../../repository";
import Collapsible from "react-collapsible";
import { Icon } from "../../../utils/Icon";

interface OnClickThirdpartiesProps {
    thirdparties?: IThirdParty[];
}

const OnClickThirdparties = (props: OnClickThirdpartiesProps) => {
    const [isExpanded , setIsExpanded] = useState(false)

    return (<div className="analysisItem" >
        <Collapsible 
            onOpening={()=>setIsExpanded(true)}
            onClosing={()=>setIsExpanded(false)}
            trigger={<OnClickThirdpartiesSmall thirdparties={props.thirdparties}  expanded={isExpanded} />} >
                {props.thirdparties?.map(elem => <div key={elem.host}>{elem.host}</div>)}
        </Collapsible>
    </div>);
};


interface OnClickThirdpartiesSmallProps extends OnClickThirdpartiesProps{
    expanded: boolean
}
const OnClickThirdpartiesSmall = (props: OnClickThirdpartiesSmallProps) => {

    return <div className="analysisSmall">
        <div className="summarizedInfo">{props.thirdparties?.length}</div>
        <div className="describeText"><Trans>onclickThirdPartyShort</Trans></div>
        <div className="expandable"><Icon className={(props.expanded?" expanded": " closed")} >expand</Icon></div>
    </div>;
};

export default OnClickThirdparties;
