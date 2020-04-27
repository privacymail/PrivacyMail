import { execute } from "./execute";
import { IService } from "./newsletter";

export interface IIdentity {
    approved: boolean;
    first_name: string;
    surname: string;
    gender: boolean;
    mail: string;
    service: IService;
}

export const generateIdentity = (newsletter: string = "", callback: (result?: IIdentity) => void): void => {
    let url = "identity/";
    if (newsletter) {
        const payload = {
            domain: newsletter
        };

        execute(url, "POST", payload)
            .then((result: IIdentity) => {
                callback(result);
            })
            .catch(() => callback(undefined));
    }
};
