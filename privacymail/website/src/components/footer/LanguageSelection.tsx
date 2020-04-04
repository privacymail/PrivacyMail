import React from "react";
import { Icon } from "../../utils/Icon";
import i18n from "../../i18n/i18n";

interface LanguageSelectionProps {
    isOpen: boolean;
    target: string;
}

const LanguageSelection = (props: LanguageSelectionProps) => {
    return (
        <div className="languageSelection">
            <Icon height={24}>de-DE</Icon>
            <div className="text">Deutsch</div>
            <Icon height={24}>en-US</Icon>
            <div className="text">English</div>
        </div>
    );
};
export default LanguageSelection;
