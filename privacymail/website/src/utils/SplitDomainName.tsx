import React from "react";

interface SplitDomainNameProps {
    domainName: string;
}

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
