export const clickButtonOnEnterKey = (event: React.KeyboardEvent<HTMLInputElement>, button: HTMLElement): void => {
    if (event.keyCode === 13) button.click();
};
export const clickButtonOnEnterKeyById = (event: React.KeyboardEvent<HTMLInputElement>, id: string): void => {
    const button = document.getElementById(id);
    if (button) clickButtonOnEnterKey(event, button);
};
