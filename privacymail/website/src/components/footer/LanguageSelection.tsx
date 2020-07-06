import React from "react";
import { Icon } from "../../utils/Icon";
import i18n from "../../i18n/i18n";

interface LanguageSelectionProps {
    isOpen: boolean;
    target: string;
}

const LanguageSelection = (props: LanguageSelectionProps) => {
    const changeLanguage = (lang: string): void => {
        i18n.changeLanguage(lang);
        window.location.reload();
    };

    return props.isOpen ? (
        <div className="languageSelection">
            <div className="language" onClick={() => changeLanguage("de-DE")}>
                <Icon importByFile height={24}>
                    de
                </Icon>
                <div className="text">Deutsch</div>
            </div>
            <div className="language" onClick={() => changeLanguage("en-US")}>
                <Icon importByFile height={24}>
                    en
                </Icon>
                <div className="text">English</div>
            </div>
        </div>
    ) : null;
};
export default LanguageSelection;