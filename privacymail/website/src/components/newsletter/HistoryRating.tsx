import React from "react";
import { IRating } from "../../repository";
import { Trans } from "react-i18next";
import { convertRatingToMark } from "../../utils/functions/convertRatingToMark";
import { getRatingColor } from "../../utils/functions/getRatingColor";
interface IHistoryRating {
    ratings?: IRating[];
}
const HistoryRating = (props: IHistoryRating) => {
    return (
        <>
            <div className="ratingHistory">
                <h2>
                    <Trans>analysis_ratingHistory</Trans>
                </h2>
                <div className="ratings">
                    {props.ratings?.map((rating, index) => {
                        const date = new Date(rating.date ?? 0);
                        const now = new Date();
                        const datestring =
                            date.getFullYear() === now.getFullYear()
                                ? date.getDate() + "." + date.getMonth() + "."
                                : date.getMonth() + "/" + date.getFullYear();

                        return (
                            <div key={index} className="historicRating">
                                <span
                                    className="grade"
                                    style={{ color: getRatingColor(((rating?.rating || 1) - 1) / 5) }}
                                >
                                    {convertRatingToMark(rating?.rating || -1)}
                                </span>
                                <span className="date">{datestring}</span>
                            </div>
                        );
                    })}
                </div>
            </div>
        </>
    );
};
export default HistoryRating;
