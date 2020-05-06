import React from "react";
import { Trans } from "react-i18next";
import ShareButton from "./ShareButton";
import { IRating } from "../../repository";
import { getRatingColor } from "../../utils/getRatingColor";
interface Color {
    red: number;
    green: number;
    blue: number;
}
interface PrivacyRatingProps {
    newsletter: string;
    privacyRating?: IRating;
}

const PrivacyRating = (props: PrivacyRatingProps) => {
    const dotIndex = props.newsletter.lastIndexOf(".");
    const ending = props.newsletter.slice(dotIndex, props.newsletter.length);
    const rest = props.newsletter.slice(0, dotIndex);

    const convertRatingToMark = (rating: number) => {
        switch (Math.round(rating)) {
            case 1:
                return "A";
            case 2:
                return "B";
            case 3:
                return "C";
            case 4:
                return "D";
            case 5:
                return "E";
            case 6:
                return "F";
        }
        return;
    };

    return (
        <div className="privacyRating">
            <h1>
                <Trans>analysis_privacyRating</Trans>
            </h1>
            <div className="rating" style={{ color: getRatingColor(((props.privacyRating?.rating || 1) - 1) / 5) }}>
                {props.privacyRating?.rating && convertRatingToMark(props.privacyRating?.rating)}
            </div>
            <div className="newsletterName">
                <span className="big">{rest}</span>
                <span className="small">{ending}</span>
            </div>
            <ShareButton newsletterName={props.newsletter} />
        </div>
    );
};
export default PrivacyRating;
