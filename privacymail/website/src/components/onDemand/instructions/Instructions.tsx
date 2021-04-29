import React, { useState } from "react";
import Collapsible from "react-collapsible";
import { Trans } from "react-i18next";
import Gmail from "./Gmail";
import Thunderbird from "./Thunderbird";

const Instructions = () => {
    const [selected, setSelected] = useState<string>("thunderbird");
    const [showMore, setShowMore] = useState<boolean>(false);
    return (
        <div className="onDemandInstructions">
            <Collapsible
                onOpening={() => setShowMore(true)}
                onClosing={() => setShowMore(false)}
                open={showMore}
                trigger={
                    <div className="collapsibleSmall">
                        <div>
                            <h2>
                                <Trans>onDemand_help</Trans>
                            </h2>
                        </div>

                        <button onClick={() => setShowMore(true)}>
                            <Trans>{showMore ? "showLess" : "showMore"}</Trans>
                        </button>
                    </div>
                }
            >
                <div className="instructions" onClick={e => e.stopPropagation()}>
                    <div className="selection">
                        <h3>
                            <Trans>step</Trans> 1: <Trans>onDemand_step1_headline</Trans>
                        </h3>
                        <div className="radioButton">
                            <input
                                type="radio"
                                checked={selected === "thunderbird"}
                                onChange={() => setSelected("thunderbird")}
                            />
                            <span>Thunderbird</span>
                        </div>
                        <div className="radioButton">
                            <input type="radio" checked={selected === "gmail"} onChange={() => setSelected("gmail")} />
                            <span>Gmail</span>
                        </div>
                    </div>
                    {selected === "thunderbird" && <Thunderbird />}
                    {selected === "gmail" && <Gmail />}
                    <h3>
                        <Trans>step</Trans> 3: <Trans>onDemand_step4_headline</Trans>
                    </h3>
                </div>
            </Collapsible>
        </div>
    );
};
export default Instructions;
