import React from "react";
import { Trans } from "react-i18next";
interface EmbedHeaderProps {
    embedName: string;
}
const EmbedHeadline = (props: EmbedHeaderProps) => {
    const dotIndex = props.embedName.lastIndexOf(".");
    const ending = props.embedName.slice(dotIndex, props.embedName.length);
    const rest = props.embedName.slice(0, dotIndex);
    return (
        <div className="generalInfo">
            <h1>
                <Trans>Thirdparty</Trans>
            </h1>
            <div className="newsletterName">
                <span className="big">{rest}</span>
                <span className="small">{ending}</span>
            </div>
        </div>
    );
};

export default EmbedHeadline;
