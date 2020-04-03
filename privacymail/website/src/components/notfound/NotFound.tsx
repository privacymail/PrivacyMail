import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import NewSearch from "../newsletter/NewSearch";
import { Trans } from "react-i18next";

const NotFound = () => {
    let { id } = useParams();

    return (
        <div className="notFound">
            <NewSearch currentSearch={id || ""} />
            <div className="heading thin">
                <Trans>404_heading</Trans>
            </div>
            <div className="light">
                <Trans>404_message1</Trans>
                <span className="medium">{id}</span>
                <Trans>404_message2</Trans>
            </div>
            <div className="light">
                <Trans>404_improvment</Trans>
            </div>
            <div>
                <Link to={"/identity/" + id}>
                    <button id="analizeButton">
                        <Trans>404_button</Trans>
                    </button>
                </Link>
            </div>
        </div>
    );
};
export default NotFound;
