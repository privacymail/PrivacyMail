import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { getNewsletter, INewsletter } from "../../repository";
import FaqHint from "./FaqHint";
import NewSearch from "./NewSearch";
import PrivacyRating from "./PrivacyRating";
import ShareButton from "./ShareButton";
import GerneralInfo from "./GeneralInfo";

const Newsletter = () => {
    let { id } = useParams();
    const [newsletter, setNewsletter] = useState<INewsletter>();
    useEffect(() => {
        getNewsletter(id, setNewsletter);
    }, [id]);

    return (
        <div className="newsletter">
            <NewSearch currentSearch={newsletter?.service.name || ""} />
            <FaqHint />
            <PrivacyRating privacyRating="C" newsletter={newsletter?.service.name || ""} />
            <div className="divider" />
            <GerneralInfo newsletter={newsletter} />
        </div>
    );
};
export default Newsletter;
