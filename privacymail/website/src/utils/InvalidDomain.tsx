import React, { useState, useEffect } from "react";
import { Trans } from "react-i18next";
import { Link } from "react-router-dom";
import { isDomainVaild } from "./functions/isDomainValid";
interface InvalidDomainProps {
    url?: string;
    urlPath: string;
    showHeadline?: boolean;
    buttonText?: string | JSX.Element;
}
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
