import React from "react";
import { IThirdParty } from "../../../repository";
import ColoredNumbers from "./ColoredNumbers";
import { Trans } from "react-i18next";
import ThirdpartyConnections from "./ThirdpartyConnections";
import CollapsibleItem from "../../../utils/CollapsibleItem";
import { areThirdpartiesEvil } from "../../../utils/functions/isThirdpartyEvil";

interface Category {
    name: string;
    thirdparties: IThirdParty[];
}
interface ThridpartysByCategoryProps {
    thirdparties?: IThirdParty[];
    homeUrl?: string;
    defaultPow?: number;
}
/**
 * This shows a list of thirdparties grouped by their sectors
 */
const ThridpartysByCategory = (props: ThridpartysByCategoryProps) => {
    const availableCategories: string[] = [];
    props.thirdparties?.forEach(thirdparty => {
        if (!availableCategories.includes(thirdparty.sector)) availableCategories.push(thirdparty.sector);
    });
    const categories: Category[] = availableCategories.map(
        (category): Category => {
            return {
                name: category,
                thirdparties: props.thirdparties?.filter(thirdparty => thirdparty.sector === category) || []
            };
        }
    );
    categories.sort((a, b) => {
        if (a.name === "tracker") {
            return -1;
        } else if (b.name === "tracker") {
            return 1;
        }
        if (a.name === "unknown") {
            return 1;
        } else if (b.name === "unknown") {
            return -1;
        }
        return b.thirdparties.length - a.thirdparties.length;
    });

    return (
        <div className="connections">
            {categories.map(category => (
                <Category {...category} key={category.name} homeUrl={props.homeUrl} defaultPow={props.defaultPow} />
            ))}
        </div>
    );
};
interface CategoryProps extends Category {
    homeUrl?: string;
    defaultPow?: number;
}
/**
 * This shows a list of all thirdparties in a sinlge sector
 */
const Category = (props: CategoryProps) => {
    return (
        <CollapsibleItem>
            <div className="category">
                <ColoredNumbers
                    number={props.thirdparties.length}
                    pow={areThirdpartiesEvil(props.thirdparties) ? 0.9 : props.defaultPow ?? 0.5}
                />
                <div className="name">
                    <Trans>{"sector_" + props.name}</Trans>
                </div>
            </div>

            <ThirdpartyConnections thirdparties={props.thirdparties} homeUrl={props.homeUrl} />
        </CollapsibleItem>
    );
};
export default ThridpartysByCategory;
