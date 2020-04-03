import React from "react";
import { Trans } from "react-i18next";
import { Icon } from "../../utils/Icon";
function Footer() {
    return (
        <footer className="footer">
            <div className="">
                <div className="item">
                    <Icon height={24}>us</Icon>
                    <p>
                        <Trans>footer_language</Trans>
                    </p>
                </div>
                <div className="item">
                    <Icon height={24}>question_answer</Icon>
                    <p>
                        <Trans>footer_faq</Trans>
                    </p>
                </div>
                <div className="item">
                    <Icon height={24}>GitHub-Mark</Icon>
                    <p>
                        <Trans>footer_github</Trans>
                    </p>
                </div>
                <div className="item">
                    <Icon height={24}>alternate_email</Icon>
                    <p>
                        <Trans height={24}>footer_imprint</Trans>
                    </p>
                </div>
                <div className="item">
                    <Icon height={24}>policy</Icon>
                    <p>
                        <Trans>footer_dataProtection</Trans>
                    </p>
                </div>
                <div className="item">
                    <p className="copyright">© {new Date().getFullYear()}, PrivacyMail Team</p>
                </div>
            </div>
        </footer>
    );
}
export default Footer;
