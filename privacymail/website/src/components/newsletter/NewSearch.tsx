import React, { useState, useEffect } from "react";
import { Trans, withTranslation, WithTranslation } from "react-i18next";
import { Link, useParams, withRouter, RouteComponentProps } from "react-router-dom";
import { clickButtonOnEnterKeyById } from "../../utils/functions/onEnterKey";

interface NewSearchProps extends WithTranslation, RouteComponentProps {
    currentSearch?: string;
}
/**
 * Gives the user the opportunity to directly search for a new newsletter
 */
const NewSearch = (props: NewSearchProps) => {
    //receives id fron the url
    let { id } = useParams();
    const hasId = ["service", "serviceNotFound"].includes(props.history.location.pathname.split("/")[1]);

    //initilizes the new search with the id
    const [newsletter, setNewsletter] = useState<string>((hasId && id) || "");
    //resets new search if url changes
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
