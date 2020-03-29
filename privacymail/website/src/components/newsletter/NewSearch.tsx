import React, { useState } from "react";
import { Trans } from "react-i18next";
import { Link } from "react-router-dom";

interface NewSearchProps {
    currentSearch: string;
}

const NewSearch = (props: NewSearchProps) => {
    const [newsletter, setNewsletter] = useState<string>("");

    return (
        <div className="newSearch">
            <div>
                <input
                    type="text"
                    value={newsletter}
                    placeholder={props.currentSearch}
                    onChange={e => setNewsletter(e.target.value)}
                />
                <Link to={"/service/" + newsletter}>
                    <button>
                        <Trans>home_analyise</Trans>
                    </button>
                </Link>
            </div>
        </div>
    );
};
export default NewSearch;
