import React, { useState, useEffect } from "react";
import { useParams, withRouter, RouteComponentProps } from "react-router-dom";
import FaqHint from "../newsletter/FaqHint";
import GerneralInfo from "../newsletter/GeneralInfo";
import AnalysisEmbed from "./AnalysisEmbed";
import { getEmbed, IEmbed } from "../../repository";

interface EmbedProps extends RouteComponentProps {}

const Embed = (props: EmbedProps) => {
    let { id } = useParams();
    const [embed, setEmbed] = useState<IEmbed>();
    useEffect(() => {
        getEmbed(id, props.history, setEmbed);
    }, [id, props.history]);

    return (
        <div className="newsletter">
            <FaqHint />
            <GerneralInfo entity={embed?.embed} />
            <div className="divider" />
            <AnalysisEmbed embed={embed} />
        </div>
    );
};
export default withRouter(Embed);
