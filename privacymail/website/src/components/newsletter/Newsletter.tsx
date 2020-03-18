import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { getNewsletter, INewsletter } from "../../repository";
import FaqHint from "./FaqHint";
import NewSearch from "./NewSearch";
import PrivacyRating from "./PrivacyRating";

const Newsletter = () => {
    let { id } = useParams();
    const [newsletter, setNewsletter] = useState<INewsletter>();
    useEffect(() => {
        getNewsletter(id, setNewsletter);
    }, [id]);

    return (
        <div className="newsletter">
            <NewSearch currentSearch={id || ""} />
            <FaqHint />
            <PrivacyRating />
            {JSON.stringify(newsletter)}
        </div>
    );
};
export default Newsletter;
