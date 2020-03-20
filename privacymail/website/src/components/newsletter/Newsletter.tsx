import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { getNewsletter, INewsletter } from "../../repository";
import FaqHint from "./FaqHint";
import NewSearch from "./NewSearch";
import PrivacyRating from "./PrivacyRating";
import ShareButton from "./ShareButton";

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
            <PrivacyRating privacyRating="C" newsletter={id || ""} />
            <div className="divider" />
        </div>
    );
};
export default Newsletter;
