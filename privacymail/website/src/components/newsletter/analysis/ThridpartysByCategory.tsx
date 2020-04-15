import React from "react";
import { IThirdParty } from "../../../repository";
import ColoredNumbers from "./ColoredNumbers";
import { Trans } from "react-i18next";
import ThirdpartyConnections from "./ThirdpartyConnections";
import CollapsibleItem from "../../../utils/CollapsibleItem";

interface Category {
    name: string;
    thirdparties: IThirdParty[];
}
interface ThridpartysByCategoryProps {
    thirdparties?: IThirdParty[];
    homeUrl?: string;
}
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
    categories.sort((a, b) => b.thirdparties.length - a.thirdparties.length);

    return (
        <div className="connections">
            {categories.map(category => (
                <Category {...category} key={category.name} homeUrl={props.homeUrl} />
            ))}
        </div>
    );
};
interface CategoryProps extends Category {
    homeUrl?: string;
}
const Category = (props: CategoryProps) => {
    return (
        <CollapsibleItem defaultOpen>
            <div className="category">
                <ColoredNumbers number={props.thirdparties.length} />
                <div className="name">
                    <Trans>{"sector_" + props.name}</Trans>
                </div>
            </div>

            <ThirdpartyConnections thirdparties={props.thirdparties} homeUrl={props.homeUrl} />
        </CollapsibleItem>
    );
};
export default ThridpartysByCategory;
