import React from "react";
import { Trans } from "react-i18next";
import ShareButton from "./ShareButton";
import { IRating } from "../../repository";
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

    const getRatingColor = (fadeFraction: number) => {
        let color1 = { red: 76, green: 175, blue: 80 };
        let color2 = { red: 251, green: 192, blue: 45 };
        let color3 = { red: 227, green: 65, blue: 52 };
        let fade = fadeFraction;

        // Do we have 3 colors for the gradient? Need to adjust the params.

        fade = fade * 2;

        // Find which interval to use and adjust the fade percentage
        if (fade >= 1) {
            fade -= 1;
            color1 = color2;
            color2 = color3;
        }

        let diffRed = color2.red - color1.red;
        let diffGreen = color2.green - color1.green;
        let diffBlue = color2.blue - color1.blue;

        let gradient = {
            red: Math.floor(color1.red + diffRed * fade),
            green: Math.floor(color1.green + diffGreen * fade),
            blue: Math.floor(color1.blue + diffBlue * fade)
        };

        return "rgb(" + gradient.red + "," + gradient.green + "," + gradient.blue + ")";
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
