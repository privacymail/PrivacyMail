export const getRatingColor = (fadeFraction: number) => {
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
