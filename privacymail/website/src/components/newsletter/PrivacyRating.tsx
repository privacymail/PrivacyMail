import React from "react";
import { Trans } from "react-i18next";
import ShareButton from "./ShareButton";

interface PrivacyRatingProps {
    newsletter: string;
    privacyRating: string;
}

const PrivacyRating = (props: PrivacyRatingProps) => {
    const dotIndex = props.newsletter.lastIndexOf(".");
    const ending = props.newsletter.slice(dotIndex, props.newsletter.length);
    const rest = props.newsletter.slice(0, dotIndex);
    return (
        <div className="privacyRating">
            <h1>
                <Trans>privacyRating</Trans>
            </h1>
            <div className="rating">{props.privacyRating}</div>
            <div className="newsletterName">
                <span className="big">{rest}</span>
                <span className="small">{ending}</span>
            </div>
            <ShareButton />
        </div>
    );
};
export default PrivacyRating;
