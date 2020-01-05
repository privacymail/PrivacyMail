import React from "react";
import { Trans, useTranslation } from "react-i18next";

function Home() {
    const { t } = useTranslation();
    return (
        <div className="home grid">
            <div></div>
            <h1 className="grid-item light">
                <Trans>home_headline</Trans>
            </h1>
            <h3 className="grid-item light">
                <Trans>home_subheadline</Trans>
            </h3>
            <div className="grid-divider" />
            <div className="grid-item input">
                <input type="text" placeholder={t("home_inputPlaceholder")} />
            </div>
            <div className="grid-item">
                <button>
                    <Trans>home_analyise</Trans>
                </button>
            </div>
            <div className="grid-divider" />
            <div className="grid-item-4">
                <p className="medium">69.933</p>
                <p className="regular">
                    <Trans>home_emailsAnalysied</Trans>
                </p>
            </div>
            <div className="grid-item-4">
                <p className="medium">2.928</p>
                <p className="regular">
                    <Trans>home_found3rdPraties</Trans>
                </p>
            </div>
            <div className="grid-item-4">
                <p className="medium highlighted">1.363</p>
                <p className="regular">
                    <Trans>home_registeredNewsletters</Trans>
                </p>
            </div>

            <div className="grid-divider" />
            <h2 className="grid-item regular">
                <Trans>home_shiningALight</Trans>
            </h2>
        </div>
    );
}

export default Home;
