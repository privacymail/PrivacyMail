import React from "react";
import { useParams, Link } from "react-router-dom";
import { Trans } from "react-i18next";

const EmbedNotFound = () => {
    let { id } = useParams();

    return (
        <div className="notFound">
            <div className="heading thin">
                <Trans>404_heading</Trans>
            </div>
            <div className="light">
                <Trans>404_message1</Trans>
                <span className="medium">{id}</span>
                <Trans>404_message2</Trans>
            </div>
        </div>
    );
};
export default EmbedNotFound;
