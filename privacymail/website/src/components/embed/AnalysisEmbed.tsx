import React from "react";
import { Trans } from "react-i18next";
import { IEmbed } from "../../repository";
import OnOpenThirdparties from "./EmbedOnOpenThirdparties";
import OnClickThirdparties from "./EmbedOnClickThirdparties";
import PersonalisedLinks from "./EmbedPersonalisedLinks";

interface AnalysisProps {
    embed?: IEmbed;
}

const AnalysisEmbed = (props: AnalysisProps) => {
    const onOpenThirdparties = props.embed?.services.filter(service => service.embed_as.includes("ONVIEW"));
    const onClickThirdparties = props.embed?.services.filter(service => service.embed_as.includes("ONCLICK"));
    return (
        <div className="analysis">
            <h1>
                <Trans>analysis_analysis</Trans>
            </h1>
            <OnOpenThirdparties
                thirdparties={onOpenThirdparties}
                homeUrl={props.embed?.embed.name}
                reliability={props.embed?.reliability.mailOpen}
            />
            <OnClickThirdparties
                thirdparties={onClickThirdparties}
                homeUrl={props.embed?.embed.name}
                reliability={props.embed?.reliability.linkClicked}
            />
            <PersonalisedLinks newsletter={props.embed} reliability={props.embed?.reliability.personalisedLinks} />
        </div>
    );
};
export default AnalysisEmbed;
