import React from "react";
import { INewsletter } from "../../repository";
import { Trans } from "react-i18next";

interface GerneralInfoProps {
    newsletter?: INewsletter;
}
const GerneralInfo = (props: GerneralInfoProps) => {

    //const [country, setCountry] = useState<string>(props.newsletter?.service.country_of_origin || "");
    //const [sector, setSector] = useState<string>( props.newsletter?.service.sector||"");

    return (
        <div className="generalInfo">
            <h1>
                <Trans>gerneralInfo</Trans>
            </h1>
            <div className="divider" />
            <div className="info" >
                <div className="row">
                    <div className="category"><Trans>sector</Trans></div>
                    <div className="value">{props.newsletter?.service.sector}</div>
                </div>
                <div className="row">
                    <div className="category"><Trans>countryOrigin</Trans></div>
                    <div className="value">{props.newsletter?.service.country_of_origin}</div>
                </div>
                <div className="row">
                    <div className="category"><Trans>analyzedMails</Trans></div>
                    <div className="value">{props.newsletter?.count_mails}</div>
                </div>
                <div className="row">
                    <div className="category"><Trans>confirmedIdentitys</Trans></div>
                    <div className="value">{props.newsletter?.num_different_idents}</div>
                </div>
            </div>
        </div>
    );
};
export default GerneralInfo;
