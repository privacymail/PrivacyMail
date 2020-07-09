import React, { useState } from "react";
import { Icon } from "../../utils/Icon";
import i18n from "../../i18n/i18n";
import { Trans } from "react-i18next";

interface LanguageSelectionPopoverProps {
    isOpen: boolean;
    target: string;
}
/**
 * This is the actual Language selection.
 * Here the user Selects the new Language.
 * This is a Popover thats displayed above the original language icon
 */
const LanguageSelectionPopover = (props: LanguageSelectionPopoverProps) => {
    /**
     * Changes the language of the user
     * @param lang The new language
     */
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

/**
 * With this the user can change its language
 */
const LanguageSelection = () => {
    const [isLanguageSelectionOpen, setLanguageSelectionOpen] = useState(false);

    /**
     * Listens for a click to close language selection
     */
    const onOutsideClick = () => {
        setLanguageSelectionOpen(false);
        window.removeEventListener("click", onOutsideClick);
    };
    /**
     * opens the language selection
     */
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
        <div className="item" onClick={e => openLanguageSelection(e)} id="languageSelection">
            <Icon height={24} importByFile>
                {i18n.language.split("-")[0]}
            </Icon>
            <div className="text">
                <Trans>footer_language</Trans>
            </div>
            <LanguageSelectionPopover isOpen={isLanguageSelectionOpen} target="" />
        </div>
    );
};
export default LanguageSelection;
