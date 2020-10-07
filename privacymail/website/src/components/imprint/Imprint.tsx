import React from "react";
import { Trans } from "react-i18next";

/**
 * This is the Imprint
 */
const Imprint = () => {
    return (
        <div className="imprint">
            <h1>
                <Trans>imprint</Trans>
            </h1>

            <h3>
                <Trans>imprint_headline1</Trans>
            </h3>
            <p>
                <Trans>imprint_data1</Trans>
            </p>

            <h2>
                <Trans>imprint_headline2</Trans>
            </h2>
            <p className="text">
                <Trans>imprint_disclaimer1</Trans>
            </p>
            <p>
                <Trans>imprint_data6</Trans>
            </p>

            <h2>
                <Trans>imprint_headline3</Trans>
            </h2>
            <h3>
                <Trans>imprint_headline7</Trans>
            </h3>
            <p>
                <Trans>imprint_data2</Trans>
            </p>

            <h2>
                <Trans>imprint_headline4</Trans>
            </h2>
            <p>
                <Trans>imprint_data3</Trans>
            </p>

            <h2>
                <Trans>imprint_headline5</Trans>
            </h2>
            <p className="text">
                <Trans>imprint_data4</Trans>
            </p>

            <h2>
                <Trans>imprint_headline6</Trans>
            </h2>
            <p>
                <Trans>imprint_data5</Trans>
            </p>
        </div>
    );
};

export default Imprint;
