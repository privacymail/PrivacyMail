export const execute = (path: string, method: string = "GET", payload: any = {}): Promise<any> => {
    const options: any = {
        method,
        headers: { "Content-Type": "application/json;charset=utf-8" }
    };
    if (method !== "GET") {
        options.body = payload;
    }
    let url = "";
    /* let url = "http://" + process.env.REACT_APP_BACKEND_URL + ":" + process.env.REACT_APP_BACKEND_PORT + "/";
 
     if (process.env.REACT_APP_BACKEND_API_PATH) {
         url += process.env.REACT_APP_BACKEND_API_PATH + "/"
     }*/

    if (!path.startsWith("/")) {
        path = "/" + path;
    }
    url += path;
    console.log(url);

    return new Promise<any>((resolve, reject) => {
        fetch(url, options)
            .then(async response => {
                if (response.status >= 400) {
                    reject(response);
                    return;
                }
                const json = await response.json();
                if (json.error || json.exeption) {
                    console.error(json.error || json.exeption);
                    reject(json.error || json.exeption);
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
