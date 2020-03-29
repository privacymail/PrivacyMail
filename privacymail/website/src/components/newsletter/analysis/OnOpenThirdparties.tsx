import React, { useState } from "react";
import { Trans } from "react-i18next";
import { IThirdParty } from "../../../repository";
import Collapsible from "react-collapsible";
import { Icon } from "../../../utils/Icon";
import ThirdpartyConnections from "./ThirdpartyConnections";

interface OnClickThirdpartiesProps {
    thirdparties?: IThirdParty[];
    homeUrl?: string;
}

const OnOpenThirdparties = (props: OnClickThirdpartiesProps) => {
    const [isExpanded, setIsExpanded] = useState(false);

    return (
        <div className="analysisItem">
            <Collapsible
                onOpening={() => setIsExpanded(true)}
                onClosing={() => setIsExpanded(false)}
                trigger={<OnOpenThirdpartiesSmall thirdparties={props.thirdparties} expanded={isExpanded} />}
            >
                <div className="analysisBig">
                    <div>
                        <h2>
                            <Trans>analysis_problemHeadline</Trans>
                        </h2>
                        <p>
                            <Trans>analysis_problemOnClick</Trans>
                        </p>
                    </div>

                    <div className="divider" />

                    <div>
                        <h2>
                            <Trans>analysis_methode</Trans>
                        </h2>
                        <div className="methodeChip">
                            <Trans>analysis_reliable</Trans>
                        </div>
                        <div className="methodeChip">
                            <Trans>analysis_noPotentialMistakes</Trans>
                        </div>
                    </div>

                    <div className="divider" />
                    <h2>
                        <Trans>analysis_connections</Trans>
                        <ThirdpartyConnections thirdparties={props.thirdparties} homeUrl={props.homeUrl} />
                    </h2>
                </div>
            </Collapsible>
        </div>
    );
};

interface OnClickThirdpartiesSmallProps extends OnClickThirdpartiesProps {
    expanded: boolean;
}
const OnOpenThirdpartiesSmall = (props: OnClickThirdpartiesSmallProps) => {
    return (
        <div className="analysisSmall">
            <div className="summarizedInfo">{props.thirdparties?.length}</div>
            <div className="describeText">
                <Trans>analysis_onopenThirdPartyShort</Trans>
            </div>
            <div className="expandable">
                <Icon className={props.expanded ? " expanded" : " closed"}>expand</Icon>
            </div>
        </div>
    );
};

export default OnOpenThirdparties;
