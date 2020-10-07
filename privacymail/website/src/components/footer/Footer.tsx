import React from "react";
import { Trans } from "react-i18next";
import { Icon } from "../../utils/Icon";
import { Link } from "react-router-dom";
import LanguageSelection from "./LanguageSelection";
/**
 * Defines the Footer of PrivacyMail
 */
function Footer() {
    return (
        <footer className="footer">
            <div className="footerFlex">
                <LanguageSelection />
                <Link to="/faq">
                    <div className="item">
                        <Icon height={24}>question_answer</Icon>
                        <div className="text">
                            <Trans>footer_faq</Trans>
                        </div>
                    </div>
                </Link>
                <a href="https://github.com/PrivacyMail/PrivacyMail" target="_blank" rel="noopener noreferrer">
                    <div className="item">
                        <Icon height={24}>github</Icon>
                        <div className="text">
                            <Trans>footer_github</Trans>
                        </div>
                    </div>
                </a>
                <Link to="/imprint">
                    <div className="item">
                        <Icon height={24}>alternate_email</Icon>
                        <div className="text">
                            <Trans height={24}>footer_imprint</Trans>
                        </div>
                    </div>
                </Link>
                <Link to="/privacy">
                    <div className="item">
                        <Icon height={24}>policy</Icon>
                        <div className="text">
                            <Trans>footer_dataProtection</Trans>
                        </div>
                    </div>
                </Link>
                <div className="item">
                    <div className="text copyright">© {new Date().getFullYear()}, PrivacyMail Team</div>
                </div>
            </div>
        </footer>
    );
}
export default Footer;
