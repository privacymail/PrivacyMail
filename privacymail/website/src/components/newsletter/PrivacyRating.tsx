import React from "react";
import { Trans } from "react-i18next";
import ShareButton from "./ShareButton";
import { IRating } from "../../repository";
import { getRatingColor } from "../../utils/functions/getRatingColor";
import SplitDomainName from "../../utils/SplitDomainName";
import { convertRatingToMark } from "../../utils/functions/convertRatingToMark";
interface Color {
    red: number;
    green: number;
    blue: number;
}
interface PrivacyRatingProps {
    newsletter: string;
    privacyRating?: IRating;
}
/**
 * Displayes the PrivacyRating
 */
const PrivacyRating = (props: PrivacyRatingProps) => {
    const grade = convertRatingToMark(props.privacyRating?.rating || -1);
    return (
        <div className="privacyRating">
            <h1>
                <Trans>analysis_privacyRating</Trans>
            </h1>
            <div className="rating" style={{ color: getRatingColor(((props.privacyRating?.rating || 1) - 1) / 5) }}>
                {props.privacyRating?.rating && grade}
            </div>
            <SplitDomainName domainName={props.newsletter} />
            <ShareButton newsletterName={props.newsletter} rating={grade || ""} />
        </div>
    );
};
export default PrivacyRating;
