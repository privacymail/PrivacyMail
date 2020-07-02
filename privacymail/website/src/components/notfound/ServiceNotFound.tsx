import React from "react";
import { useParams, Link } from "react-router-dom";
import { Trans } from "react-i18next";
import InvalidDomain from "../../utils/InvalidDomain";
import { isDomainVaild } from "../../utils/functions/isDomainValid";

const ServiceNotFound = () => {
    let { id } = useParams();

    return (
        <div className="notFound">
            <div className="heading thin">
                <Trans>404_heading</Trans>
            </div>

            {isDomainVaild(id || "") ? (
                <>
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
                </>
            ) : (
                <InvalidDomain
                    url={id}
                    urlPath="service"
                    showHeadline={false}
                    buttonText={<Trans>home_analyise</Trans>}
                />
            )}
        </div>
    );
};
export default ServiceNotFound;
