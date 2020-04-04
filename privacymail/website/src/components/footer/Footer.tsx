import React from "react";
import { Trans } from "react-i18next";
import { Icon } from "../../utils/Icon";
function Footer() {
    return (
        <footer className="footer">
            <div className="">
                <div className="item">
                    <Icon height={24}>us</Icon>
                    <div className="text">
                        <Trans>footer_language</Trans>
                    </div>
                </div>
                <div className="item">
                    <Icon height={24}>question_answer</Icon>
                    <div className="text">
                        <Trans>footer_faq</Trans>
                    </div>
                </div>
                <div className="item">
                    <Icon height={24}>GitHub-Mark</Icon>
                    <div className="text">
                        <Trans>footer_github</Trans>
                    </div>
                </div>
                <div className="item">
                    <Icon height={24}>alternate_email</Icon>
                    <div className="text">
                        <Trans height={24}>footer_imprint</Trans>
                    </div>
                </div>
                <div className="item">
                    <Icon height={24}>policy</Icon>
                    <div className="text">
                        <Trans>footer_dataProtection</Trans>
                    </div>
                </div>
                <div className="item">
                    <div className="text copyright">© {new Date().getFullYear()}, PrivacyMail Team</div>
                </div>
            </div>
        </footer>
    );
}
export default Footer;
