import React, { useState, useEffect } from "react";
import { Trans } from "react-i18next";
import { Link } from "react-router-dom";
import { isDomainVaild } from "./functions/isDomainValid";
interface InvalidDomainProps {
    url?: string; //initial Domain
    urlPath: string; //the urlPath where the analyse button will take the use
    showHeadline?: boolean; //this option will toggle a headline
    buttonText?: string | JSX.Element; //custon Buttontext for the analyse button
}
/**
 * Provides an DomainInputElement that checks if a domain is valid
 */
const InvalidDomain = (props: InvalidDomainProps) => {
    const [url, setUrl] = useState<string>(props.url || "");
    let urlPath = props.urlPath;
    if (!urlPath.startsWith("/")) {
        urlPath = "/" + urlPath;
    }
    if (!urlPath.endsWith("/")) {
        urlPath = urlPath + "/";
    }
    useEffect(() => {
        if (props.url) setUrl(props.url);
    }, [props.url]);
    return (
        <div className="invalid">
            {props.showHeadline && (
                <h2>
                    <Trans>identity_invalid_domain</Trans>
                </h2>
            )}
            <div>
                <p>
                    <Trans i18nKey="identity_invalid_text">
                        <span className="medium">{{ domain: props.url }}</span>
                    </Trans>
                </p>
                <div>
                    <input value={url} onChange={e => setUrl(e.target.value)} />
                    <div className={isDomainVaild(url) ? "" : "disabledButton"}>
                        <Link to={urlPath + url}>
                            <button id="analizeButton">{props.buttonText || <Trans>404_button</Trans>}</button>
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    );
};
export default InvalidDomain;
