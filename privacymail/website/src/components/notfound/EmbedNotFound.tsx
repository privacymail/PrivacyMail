import React from "react";
import { useParams } from "react-router-dom";
import { Trans } from "react-i18next";
import InvalidDomain from "../../utils/InvalidDomain";

const EmbedNotFound = () => {
    let { id } = useParams();

    return (
        <div className="notFound">
            <div className="heading thin">
                <Trans>404_heading</Trans>
            </div>
            <InvalidDomain url={id} urlPath="embed" showHeadline={false} buttonText={<Trans>home_analyise</Trans>} />
        </div>
    );
};
export default EmbedNotFound;
