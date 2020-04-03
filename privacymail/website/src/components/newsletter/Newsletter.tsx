import React, { useState, useEffect } from "react";
import { useParams, withRouter } from "react-router-dom";
import { getNewsletter, INewsletter } from "../../repository";
import FaqHint from "./FaqHint";
import NewSearch from "./NewSearch";
import PrivacyRating from "./PrivacyRating";
import GerneralInfo from "./GeneralInfo";
import Analysis from "./analysis/Analysis";
import { History } from "history";
interface NewsletterProps {
    history: History;
}

const Newsletter = (props: NewsletterProps) => {
    let { id } = useParams();
    const [newsletter, setNewsletter] = useState<INewsletter>();
    useEffect(() => {
        getNewsletter(id, props.history, setNewsletter);
    }, [id, props.history]);

    return (
        <div className="newsletter">
            <NewSearch currentSearch={newsletter?.service.name || ""} />
            <FaqHint />
            <PrivacyRating privacyRating="C" newsletter={newsletter?.service.name || ""} />
            <div className="divider" />
            <GerneralInfo newsletter={newsletter} />
            <div className="divider" />
            <Analysis newsletter={newsletter} />
        </div>
    );
};
export default withRouter(Newsletter);
