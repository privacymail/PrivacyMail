import React, { useState } from "react";
import { Trans } from "react-i18next";
import { Icon } from "../../utils/Icon";
import { Link } from "react-router-dom";
import LanguageSelection from "./LanguageSelection";
import i18n from "i18next";

function Footer() {
    const [isLanguageSelectionOpen, setLanguageSelectionOpen] = useState(false);

    const onOutsideClick = () => {
        setLanguageSelectionOpen(false);
        window.removeEventListener("click", onOutsideClick);
    };
    const openLanguageSelection = (e: React.MouseEvent) => {
        e.stopPropagation();

        if (!isLanguageSelectionOpen) {
            setLanguageSelectionOpen(true);
            window.addEventListener("click", onOutsideClick);
        } else {
            onOutsideClick();
        }
    };

    return (
        <footer className="footer">
            <div className="footerFlex">
                <div className="item" onClick={e => openLanguageSelection(e)} id="languageSelection">
                    <Icon height={24}>{i18n.language}</Icon>
                    <div className="text">
                        <Trans>footer_language</Trans>
                    </div>
                    <LanguageSelection isOpen={isLanguageSelectionOpen} target="" />
                </div>
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
                        <Icon height={24}>GitHub-Mark</Icon>
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
