import React, { useState, useEffect } from "react";
import { useParams, withRouter, RouteComponentProps } from "react-router-dom";
import { getNewsletter, INewsletter } from "../../repository";
import FaqHint from "./FaqHint";
import PrivacyRating from "./PrivacyRating";
import GerneralInfo from "./GeneralInfo";
import HistoryRating from "./HistoryRating";
import Analysis from "./analysis/Analysis";
import IdentityAlert from "./IdentityAlert";
import NoEmailAlert from "./NoEmailAlert";
import Spinner from "../../utils/Spinner";
import SplitDomainName from "../../utils/SplitDomainName";
interface NewsletterProps extends RouteComponentProps {}
/**
 * Defines the Layout of the newsletteranalysis
 */
const Newsletter = (props: NewsletterProps) => {
    let { id } = useParams<any>();
    const [newsletter, setNewsletter] = useState<INewsletter>();
    const [isLoading, setIsLoading] = useState<boolean>(true);

    /**
     * Refetched the data from the backend if the newsletter id changes
     */
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
                {/* Checks if the newsletter contains meaningfull data */}
                {newsletter?.count_mails !== 0 ||
                newsletter?.third_parties.length !== 0 ||
                newsletter?.num_different_idents !== 0 ? (
                    <>
                        <FaqHint />
                        <PrivacyRating
                            privacyRating={newsletter?.rating.newsletterRating}
                            newsletter={newsletter?.service.name || ""}
                        />
                        <HistoryRating ratings={newsletter?.rating.history} />

                        {newsletter && newsletter?.num_different_idents < 2 && (
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
                    </>
                ) : (
                    <>
                        <SplitDomainName domainName={newsletter?.service.name || ""} />
                        <NoEmailAlert newsletterName={newsletter?.service.name || ""} />
                        <div className="divider" />
                        <GerneralInfo
                            entity={newsletter?.service}
                            count_mails={newsletter?.count_mails}
                            num_different_idents={newsletter?.num_different_idents}
                            type="service"
                        />
                    </>
                )}
            </div>
        </Spinner>
    );
};
export default withRouter(Newsletter);
