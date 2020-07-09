import React, { useState } from "react";
import { Trans } from "react-i18next";
import { Link } from "react-router-dom";

/**
 * Shows a hint to our FAQ
 */
const FaqHint = () => {
    //checks if the banner was already dissmissed
    const [showBanner, setShowBanner] = useState<boolean>(
        !JSON.parse(window.localStorage.getItem("faqBannerDismissed") || "false")
    );

    /**
     * dismisses the banner
     */
    const dismissBanner = () => {
        window.localStorage.setItem("faqBannerDismissed", "true");
        setShowBanner(false);
    };

    return showBanner ? (
        <div className="faqHint">
            <div>
                <Trans>faqHint</Trans>
            </div>
            <button aria-label="Close FAQ Reminder" className="closeButton" onClick={() => dismissBanner()}>
                &times;
            </button>
            <Link to={"/faq/"}>
                <button>
                    <Trans>faq</Trans>
                </button>
            </Link>
        </div>
    ) : null;
};
export default FaqHint;
