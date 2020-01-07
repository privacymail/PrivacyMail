import React from "react";

const Parallax = props => {
    return <div className="parallax">{props.children}</div>;
};
const ParallaxBase = props => {
    return <div className="parallax-layer parallax-base">{props.children}</div>;
};
const ParallaxBackground = props => {
    return (
        <div className="parallax-layer parallax-background">
            {props.children}
        </div>
    );
};

export { Parallax, ParallaxBase, ParallaxBackground };
