import React, { useState, useEffect } from "react";
import { useParams, withRouter, RouteComponentProps } from "react-router-dom";
import { getNewsletter, INewsletter } from "../../repository";
import FaqHint from "./FaqHint";
import PrivacyRating from "./PrivacyRating";
import GerneralInfo from "./GeneralInfo";
import Analysis from "./analysis/Analysis";
import IdentityAlert from "./IdentityAlert";
import Spinner from "../../utils/Spinner";
interface NewsletterProps extends RouteComponentProps {}

const Newsletter = (props: NewsletterProps) => {
    let { id } = useParams();
    const [newsletter, setNewsletter] = useState<INewsletter>();
    const [isLoading, setIsLoading] = useState<boolean>(true);

    useEffect(() => {
        setIsLoading(true);
        getNewsletter(id, props.history, (newsletter: INewsletter) => {
            setNewsletter(newsletter);
            setIsLoading(false);
        });
    }, [id, props.history]);

    return (
        <Spinner isSpinning={isLoading}>
            <div className="newsletter">
                <FaqHint />
                <PrivacyRating privacyRating={newsletter?.rating} newsletter={newsletter?.service.name || ""} />
                {newsletter && newsletter?.num_different_idents < 3 && (
                    <IdentityAlert newsletterName={newsletter?.service.name} />
                )}
                <div className="divider" />
                <GerneralInfo
                    entity={newsletter?.service}
                    count_mails={newsletter?.count_mails}
                    num_different_idents={newsletter?.num_different_idents}
                    type="service"
                />
                <div className="divider" />
                <Analysis newsletter={newsletter} />
            </div>
        </Spinner>
    );
};
export default withRouter(Newsletter);
