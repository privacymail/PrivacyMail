import React, { useState } from "react";
import { Trans, WithTranslation, withTranslation } from "react-i18next";
import { clickButtonOnEnterKeyById } from "../../utils/onEnterKey";
import { Link } from "react-router-dom";

const Welcome = (props: WithTranslation) => {
    const [newsletter, setNewsletter] = useState<string>("");
    return (
        <div className="welcome">
            <div>
                <h1 className="light">
                    <Trans>home_headline</Trans>
                </h1>
                <h3 className="light">
                    <Trans>home_subheadline</Trans>
                </h3>
                <div className="input">
                    <div className="search">
                        <input
                            type="text"
                            value={newsletter}
                            placeholder={props.t("home_inputPlaceholder")}
                            onChange={e => setNewsletter(e.target.value)}
                            onKeyUp={e => clickButtonOnEnterKeyById(e, "analizeButton")}
                        />
                        <Link to={"/service/" + newsletter}>
                            <button id="analizeButton">
                                <Trans>home_analyise</Trans>
                            </button>
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default withTranslation()(Welcome);
