import React, { useState, useEffect } from "react";
import { useParams, withRouter, RouteComponentProps } from "react-router-dom";
import { getNewsletter, INewsletter } from "../../repository";
import FaqHint from "./FaqHint";
import PrivacyRating from "./PrivacyRating";
import GerneralInfo from "./GeneralInfo";
import Analysis from "./analysis/Analysis";
import IdentityAlert from "./IdentityAlert";
interface NewsletterProps extends RouteComponentProps {}

const Newsletter = (props: NewsletterProps) => {
    let { id } = useParams();
    const [newsletter, setNewsletter] = useState<INewsletter>();
    useEffect(() => {
        getNewsletter(id, props.history, setNewsletter);
    }, [id, props.history]);

    return (
        <div className="newsletter">
            <FaqHint />
            <PrivacyRating privacyRating="C" newsletter={newsletter?.service.name || ""} />
            {newsletter && newsletter?.num_different_idents < 3 && <IdentityAlert />}
            <div className="divider" />
            <GerneralInfo
                entity={newsletter?.service}
                count_mails={newsletter?.count_mails}
                num_different_idents={newsletter?.num_different_idents}
            />
            <div className="divider" />
            <Analysis newsletter={newsletter} />
        </div>
    );
};
export default withRouter(Newsletter);
