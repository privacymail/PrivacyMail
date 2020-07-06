import React from "react";
import { Icon } from "../../utils/Icon";
import { withTranslation, WithTranslation } from "react-i18next";
interface ShareButtonProps extends WithTranslation {
    newsletterName: string;
    rating: string;
}
const ShareButton = (props: ShareButtonProps) => {
    const navigatorAny: any = navigator;
    const triggerNativeShare = () => {
        const shareData = {
            title: window.location.hostname,
            url: window.location.href,
            text:
                props
                    .t("share_text")
                    .replace("#company", props.newsletterName)
                    .replace("#rating", props.rating) + "\n \n"
        };
        navigatorAny.share(shareData);
    };

    return navigatorAny.share ? (
        <Icon onClick={triggerNativeShare} className="shareButton">
            share
        </Icon>
    ) : null;
};
export default withTranslation()(ShareButton);
