import React from "react";
import { Trans, useTranslation } from "react-i18next";
import Instructions from "./instructions/Instructions";

interface OnDemandInputProps {
    rawEmail: string;
    setRawEmail: (email: string) => void;
    runAnalysis: () => void;
}

const OnDemandInput = (props: OnDemandInputProps) => {
    const { t } = useTranslation();
    return (
        <>
            <Instructions />
            <div className="emailInput">
                <h2>
                    <Trans>onDemand_input_headlind</Trans>
                </h2>
                <p className="alert info">
                    <Trans>onDemand_dataPrivacyInfo</Trans>
                </p>
                <textarea
                    id="text"
                    value={props.rawEmail}
                    placeholder={t("onDemand_inputPlaceholder")}
                    onChange={e => props.setRawEmail(e.target.value)}
                    rows={20}
                />
                <div className="buttonRight">
                    <button
                        onClick={e => {
                            props.runAnalysis();
                        }}
                    >
                        <Trans>home_analyise</Trans>
                    </button>
                </div>
            </div>
        </>
    );
};

export default OnDemandInput;
