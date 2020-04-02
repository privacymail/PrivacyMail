import React, { useState, useEffect } from "react";
import { Trans } from "react-i18next";
import { Link } from "react-router-dom";
import { clickButtonOnEnterKeyById } from "../../utils/onEnterKey";

interface NewSearchProps {
    currentSearch: string;
}

const NewSearch = (props: NewSearchProps) => {
    const [newsletter, setNewsletter] = useState<string>(props.currentSearch);
    useEffect(() => setNewsletter(props.currentSearch), [props.currentSearch]);

    return (
        <div className="newSearch">
            <div>
                <input
                    type="text"
                    value={newsletter}
                    placeholder={props.currentSearch}
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
export default NewSearch;
