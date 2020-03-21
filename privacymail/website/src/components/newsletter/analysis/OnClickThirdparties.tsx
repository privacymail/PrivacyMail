import React from "react";
import { Trans } from "react-i18next";
import { IThirdParty } from "../../../repository";
import Collapsible from "react-collapsible";

interface OnClickThirdpartiesProps {
    thirdparties?: IThirdParty[];
}

const OnClickThirdparties = (props: OnClickThirdpartiesProps) => {
    return (<div className="analysisItem" ><Collapsible trigger={<OnClickThirdpartiesSmall thirdparties={props.thirdparties} />} >
    {props.thirdparties?.map(elem => <div key={elem.host}>{elem.host}</div>)}
</Collapsible></div>);
};

const OnClickThirdpartiesSmall = (props: OnClickThirdpartiesProps) => {
    return <div className="analysisSmall">
        <div className="summarizedInfo">{props.thirdparties?.length}</div>
        <div className="describeText"><Trans>onclickThirdPartyShort</Trans></div>
    </div>;
};

export default OnClickThirdparties;
