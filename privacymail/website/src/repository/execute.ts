/**
 * This will execute all API calls
 * @param path this is the desination of the API Call
 * @param method  this is the HTTP Method that should be used
 * @param payload if you are using POST, PUT, etc. this will be your payload
 * @return A Promise that gets resolved or rejected as soon as the API Call is finished
 */
export const execute = (path: string, method: string = "GET", payload: any = {}): Promise<any> => {
    const options: any = {
        method,
        headers: { "Content-Type": "application/json;charset=utf-8" },
    };
    if (method !== "GET") {
        options.body = JSON.stringify(payload);
    }
    let url = "";

    //If a custom backendPath is provided it will be added to all requests
    if (process.env.REACT_APP_BACKEND_API_PATH) {
        url += "/" + process.env.REACT_APP_BACKEND_API_PATH;
    } else {
        url += "/api";
    }

    //Checks if a / is at the start of the path. If not a / will be added
    if (!path.startsWith("/")) {
        path = "/" + path;
    }
    url += path;

    /**
     * this executes the API Call.
     * If successfull the Promise will get resolved with the data form the api call.
     * If not the Promise will get rejected and an error will be thrown to the console
     */
    return new Promise<any>((resolve, reject) => {
        fetch(url, options)
            .then(async (response) => {
                if (response.status >= 400) {
                    reject(response);
                    return;
                }
                const json = await response.json();
                if (json.error || json.exeption || json.success === false) {
                    console.error(json.error || json.exeption || json);
                    reject(json.error || json.exeption || json);
                } else {
                    resolve(json);
                }
            })
            .catch((error) => {
                console.error(error);
                reject(error);
            });
    });
};
