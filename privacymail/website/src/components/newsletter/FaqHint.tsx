import React, { useState } from "react";
import { Trans } from "react-i18next";
import { Link } from "react-router-dom";

const FaqHint = () => {
    const [showBanner, setShowBanner] = useState<boolean>(!JSON.parse(window.localStorage.getItem("faqBannerDismissed") || "false"));
    console.log(showBanner);


    const dismissBanner = () => {
        window.localStorage.setItem("faqBannerDismissed", "true");
        setShowBanner(false)
    }

    return (showBanner ? (
        <div className="faqHint">
            <div><Trans>faqHint</Trans></div>
            <button aria-label="Close FAQ Reminder" className="closeButton" onClick={() => dismissBanner()}>&times;</button>
            <Link to={"/faq/"}>
                <button >
                    <Trans>faq</Trans>
                </button>
            </Link>

        </div>) : null)
}
export default FaqHint;