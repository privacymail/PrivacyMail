import React from "react";

import i18n from "../../i18n/i18n";
import faqJson from "../../i18n/faq.json";
import CollapsibleItem from "../../utils/CollapsibleItem";
import { Trans } from "react-i18next";

const FAQ = () => {
    const groups: string[] = [];
    faqJson.forEach(question => {
        if (!groups.includes(question.group)) groups.push(question.group);
    });

    const generateQuestions = (questions: any[]) => {
        const currentLanguage = i18n.language.split("-")[0];
        return questions.map(question => (
            <CollapsibleItem key={question.question[currentLanguage]}>
                <span>{question.question[currentLanguage]}</span>
                <span className="light">{question.answer[currentLanguage]}</span>
            </CollapsibleItem>
        ));
    };

    const generateGroups = (groups: string[], questions: any[]) => {
        return groups.map(group => (
            <React.Fragment key={group}>
                <h2>
                    <Trans>{group}</Trans>
                </h2>
                <div className="questions">
                    {generateQuestions(questions.filter(question => question.group === group))}
                </div>
            </React.Fragment>
        ));
    };
    return (
        <div className="faq">
            <h1>
                <Trans>faq_headline</Trans>
            </h1>
            <p>
                <Trans>faq_subheadline</Trans>
            </p>
            {generateGroups(groups, faqJson)}
        </div>
    );
};

export default FAQ;
