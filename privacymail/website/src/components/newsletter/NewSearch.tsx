import React, { useState, useEffect } from "react";
import { Trans, withTranslation, WithTranslation } from "react-i18next";
import { Link, useParams, withRouter, RouteComponentProps } from "react-router-dom";
import { clickButtonOnEnterKeyById } from "../../utils/onEnterKey";

interface NewSearchProps extends WithTranslation, RouteComponentProps {
    currentSearch?: string;
}
const NewSearch = (props: NewSearchProps) => {
    let { id } = useParams();
    const hasId = props.history.location.pathname.split("/").length > 2;

    const [newsletter, setNewsletter] = useState<string>((hasId && id) || "");
    useEffect(() => setNewsletter((hasId && id) || ""), [id, hasId]);

    const placeholder = props.currentSearch || props.t("home_inputPlaceholder");
    return (
        <div className="newSearch">
            <div>
                <input
                    type="text"
                    value={newsletter}
                    placeholder={placeholder}
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
    );
};
export default withRouter(withTranslation()(NewSearch));
