import React from "react";
import { Trans } from "react-i18next";
import SplitDomainName from "../../utils/SplitDomainName";
interface EmbedHeaderProps {
    embedName: string;
}
/**
 * This displays the Embed name
 */
const EmbedHeadline = (props: EmbedHeaderProps) => {
    return (
        <div className="generalInfo">
            <h1>
                <Trans>Thirdparty</Trans>
            </h1>
            <SplitDomainName domainName={props.embedName} />
        </div>
    );
};

export default EmbedHeadline;
