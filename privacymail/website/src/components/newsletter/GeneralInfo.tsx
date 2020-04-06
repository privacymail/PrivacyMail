import React, { useState } from "react";
import { INewsletter, postInformation } from "../../repository";
import { Trans, withTranslation, WithTranslation } from "react-i18next";

import countries from "../../i18n/countires.json";
import sectors from "../../i18n/sectors.json";
import i18n from "../../i18n/i18n";

interface GerneralInfoProps extends WithTranslation {
    newsletter?: INewsletter;
}
const GerneralInfo = (props: GerneralInfoProps) => {
    const [country, setCountry] = useState<string>(props.newsletter?.service.country_of_origin || "");
    const [sector, setSector] = useState<string>(props.newsletter?.service.sector || "");

    const getCurrentItemTranslation = (arr: any[], key?: string) => {
        const currentLanguage = i18n.language.split("-")[0];
        const trans = arr.find((elem: any) => elem.key === key);

        return trans?.[currentLanguage];
    };

    const generateOptions = (arr: any[]) => {
        const currentLanguage = i18n.language.split("-")[0];
        const newArray = arr
            .sort((a: any, b: any) => {
                return a[currentLanguage] < b[currentLanguage] ? -1 : 1;
            })
            .map(elem => (
                <option key={elem.key} value={elem.key}>
                    {elem[currentLanguage]}
                </option>
            ));
        newArray.push(
            <option key="empty" value="" disabled hidden>
                {props.t("pleaseSelect")}
            </option>
        );
        return newArray;
    };

    const editalble =
        props.newsletter?.service.sector === "unknown" && props.newsletter?.service.country_of_origin === "";
    return (
        <div className="generalInfo">
            <h1>
                <Trans>analysis_gerneralInfo</Trans>
            </h1>
            <div className="alert">
                <Trans>analysis_editDisclaimer</Trans>
            </div>

            <div className="divider" />
            <div className="info">
                <div className="row">
                    <div className="category">
                        <Trans>analysis_sector</Trans>
                    </div>
                    <div className="value">
                        {editalble ? (
                            <select value={sector} onChange={e => setSector(e.target.value)}>
                                {generateOptions(sectors)}
                            </select>
                        ) : (
                            getCurrentItemTranslation(sectors, props.newsletter?.service.sector)
                        )}
                    </div>
                </div>
                <div className="row">
                    <div className="category">
                        <Trans>analysis_countryOrigin</Trans>
                    </div>
                    <div className="value">
                        {editalble ? (
                            <select value={country} onChange={e => setCountry(e.target.value)}>
                                {generateOptions(countries)}
                            </select>
                        ) : (
                            getCurrentItemTranslation(sectors, props.newsletter?.service.country_of_origin)
                        )}
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
            {editalble && (
                <div className="submit">
                    <button onClick={() => postInformation(props.newsletter?.service.name, sector, country)}>
                        <Trans>submit</Trans>
                    </button>
                </div>
            )}
        </div>
    );
};
export default withTranslation()(GerneralInfo);
