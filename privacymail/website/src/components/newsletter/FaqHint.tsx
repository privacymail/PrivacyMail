import React from "react";
import { Trans } from "react-i18next";
import { Link } from "react-router-dom";

const FaqHint = () => {
    return (
        <div className="faqHint">
            <div><Trans>faqHint</Trans></div>
            <button aria-label="Close FAQ Reminder" className="closeButton">&times;</button>
            <Link to={"/faq/"}>
                <button >
                    <Trans>faq</Trans>
                </button>
            </Link>

        </div>)
}
export default FaqHint;