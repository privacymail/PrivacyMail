/**
 * clicks a button if the enter key is pressed
 * @param event the key event
 * @param button the button to be clicked
 */
export const clickButtonOnEnterKey = (event: React.KeyboardEvent<HTMLInputElement>, button: HTMLElement): void => {
    if (event.keyCode === 13) button.click();
};

/**
 * clicks a button if the enter key is pressed
 * @param event the key event
 * @param button the id of the button to be clicked
 */
export const clickButtonOnEnterKeyById = (event: React.KeyboardEvent<HTMLInputElement>, id: string): void => {
    const button = document.getElementById(id);
    if (button) clickButtonOnEnterKey(event, button);
};
