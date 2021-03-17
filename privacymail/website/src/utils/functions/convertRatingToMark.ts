/**
 * Converts a numerical rating to the letter scale
 * @param rating rating of the newsletter
 */
export const convertRatingToMark = (rating: number) => {
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
