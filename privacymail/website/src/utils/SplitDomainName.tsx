import React from "react";

interface SplitDomainNameProps {
    domainName: string;
}
/**
 * This splits a domainname in a way that the TLD is not emphasized while the company name is
 */
const SplitDomainName = (props: SplitDomainNameProps) => {
    const dotIndex = props.domainName.lastIndexOf(".");
    const ending = props.domainName.slice(dotIndex, props.domainName.length);
    const rest = props.domainName.slice(0, dotIndex);
    return (
        <div className="newsletterName">
            <span className="big">{rest}</span>
            <span className="small">{ending}</span>
        </div>
    );
};
export default SplitDomainName;
