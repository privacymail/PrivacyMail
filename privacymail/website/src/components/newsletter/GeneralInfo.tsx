import React from "react";
import { INewsletter } from "../../repository";
import { Trans } from "react-i18next";

import countries from "../../i18n/countires.json";
import sectors from "../../i18n/sectors.json";
import i18n from "../../i18n/i18n";

interface GerneralInfoProps {
    newsletter?: INewsletter;
}
const GerneralInfo = (props: GerneralInfoProps) => {
    //const [country, setCountry] = useState<string>(props.newsletter?.service.country_of_origin || "");
    //const [sector, setSector] = useState<string>( props.newsletter?.service.sector||"");

    const getCurrentItemTranslation = (arr: any[], key?: string) => {
        const currentLanguage = i18n.language.split("-")[0];
        const trans = arr.find((elem: any) => elem.key === key);

        return trans?.[currentLanguage];
    };

    return (
        <div className="generalInfo">
            <h1>
                <Trans>analysis_gerneralInfo</Trans>
            </h1>
            <div className="divider" />
            <div className="info">
                <div className="row">
                    <div className="category">
                        <Trans>analysis_sector</Trans>
                    </div>
                    <div className="value">{getCurrentItemTranslation(sectors, props.newsletter?.service.sector)}</div>
                </div>
                <div className="row">
                    <div className="category">
                        <Trans>analysis_countryOrigin</Trans>
                    </div>
                    <div className="value">
                        {getCurrentItemTranslation(countries, props.newsletter?.service.country_of_origin)}
                    </div>
                </div>
                <div className="row">
                    <div className="category">
                        <Trans>analysis_analyzedMails</Trans>
                    </div>
                    <div className="value">{props.newsletter?.count_mails}</div>
                </div>
                <div className="row">
                    <div className="category">
                        <Trans>analysis_confirmedIdentitys</Trans>
                    </div>
                    <div className="value">{props.newsletter?.num_different_idents}</div>
                </div>
            </div>
        </div>
    );
};
export default GerneralInfo;
