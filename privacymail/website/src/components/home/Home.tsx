import React from "react";
import Welcome from "./Welcome";
import Statistics from "./Statistics";
import WhatWeDo from "./WhatWeDo";
import Tracking from "./Tracking";
import WhyPrivacymail from "./WhyPrivacymail";
import Detection from "./Detection";

const Home = () => {
    return (
        <div className="home">
            <Welcome />
            <div className="details">
                <Statistics />

                <WhatWeDo />

                <WhyPrivacymail />
                <Detection />
                <Tracking />
            </div>
        </div>
    );
};

export default Home;
