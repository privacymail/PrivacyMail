export const execute = (path: string, method: string = "GET", payload: any = {}): Promise<any> => {
    const options: any = {
        method,
        headers: { "Content-Type": "application/json;charset=utf-8" }
    };
    if (method !== "GET") {
        options.body = JSON.stringify(payload);
    }
    let url = "";
    /* let url = "http://" + process.env.REACT_APP_BACKEND_URL + ":" + process.env.REACT_APP_BACKEND_PORT + "/";
     */

    if (process.env.REACT_APP_BACKEND_API_PATH) {
        url += "/" + process.env.REACT_APP_BACKEND_API_PATH;
    }

    if (!path.startsWith("/")) {
        path = "/" + path;
    }
    url += path;

    return new Promise<any>((resolve, reject) => {
        fetch(url, options)
            .then(async response => {
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
            .catch(error => {
                console.error(error);
                reject(error);
            });
    });
};
