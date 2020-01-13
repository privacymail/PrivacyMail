import React from "react";
import { Trans } from "react-i18next";
function Footer() {
    return (
        <div className="footer">
            <div className="grid">
                <div className="grid-item-4">
                    <Trans>footer_language</Trans>
                </div>
                <div className="grid-item-4">
                    <Trans>footer_faq</Trans>
                </div>
                <div className="grid-item-4">
                    <Trans>footer_github</Trans>
                </div>
                <div className="grid-item-4">
                    <Trans>footer_imprint</Trans>
                </div>
                <div className="grid-item-4">
                    <Trans>footer_dataProtection</Trans>
                </div>
            </div>
        </div>
    );
}
export default Footer;
