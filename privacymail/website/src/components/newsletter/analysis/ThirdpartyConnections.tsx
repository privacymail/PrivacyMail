import React from "react";
import { IThirdParty } from "../../../repository";
import { Link } from "react-router-dom";
import { Icon } from "../../../utils/Icon";
import { Trans } from "react-i18next";

interface ThirdpartyConnectionsProps {
    thirdparties?: IThirdParty[];
    homeUrl?: string;
    linkTo?: string;
}
const ThirdpartyConnections = (props: ThirdpartyConnectionsProps) => {
    return (
        <ul>
            {props.thirdparties
                ?.sort((a, b) => {
                    if (a.name === props.homeUrl) return -1;
                    if (b.name === props.homeUrl) return 1;

                    if (a.receives_identifier !== b.receives_identifier) {
                        if (a.receives_identifier) return -1;
                        if (b.receives_identifier) return 1;
                    }

                    return a.name < b.name ? -1 : 1;
                })
                .map((thirdparty, index) => (
                    <Thirdparty
                        key={index}
                        thirdparty={thirdparty}
                        isHomeUrl={thirdparty.name === props.homeUrl}
                        linkTo={props.linkTo}
                    />
                ))}
        </ul>
    );
};

interface ThirdpartyProps {
    thirdparty: IThirdParty;
    isHomeUrl: boolean;
    linkTo?: string;
}
const Thirdparty = (props: ThirdpartyProps) => {
    return (
        <li className="thirdparty">
            <Link to={(props.linkTo || "/embed") + "/" + props.thirdparty.name}>{props.thirdparty.name}</Link>
            <div className="icons">
                {props.isHomeUrl && <Icon>home</Icon>}
                {props.thirdparty.receives_identifier && (
                    <Icon title={<Trans>thirdparty_receivesLeak</Trans>}>danger</Icon>
                )}
            </div>
        </li>
    );
};

export default ThirdpartyConnections;
