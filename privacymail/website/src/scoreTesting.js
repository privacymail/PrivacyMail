const fs = require("fs");
const prettier = require("prettier");
const prettierConfig = require("../package.json").prettier;
const fetch = require("node-fetch");

const execute = (path, method = "GET", payload = {}) => {
    const options = {
        method,
        headers: { "Content-Type": "application/json;charset=utf-8" }
    };
    if (method !== "GET") {
        options.body = JSON.stringify(payload);
    }
    /* let url = "http://" + process.env.REACT_APP_BACKEND_URL + ":" + process.env.REACT_APP_BACKEND_PORT + "/";
     */
    console.log(path);

    return new Promise((resolve, reject) => {
        fetch(path, options)
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

const executeFetches = async () => {
    const results = [];

    for (let i = 1; i < 1000; i++) {
        try {
            const url = "http://localhost:8000/api/service/" + i;
            results.push((await execute(url)).rating);
        } catch (error) {
            console.log("Failed for ", i);
        }
    }

    const stats = {
        A: 0,
        B: 0,
        C: 0,
        D: 0,
        E: 0,
        F: 0,
        avg: 0
    };

    results.forEach(result => {
        switch (Math.round(result.rating)) {
            case 1:
                stats.A = stats.A + 1;
                break;
            case 2:
                stats.B = stats.B + 1;
                break;
            case 3:
                stats.C = stats.C + 1;
                break;
            case 4:
                stats.D = stats.D + 1;
                break;
            case 5:
                stats.E = stats.E + 1;
                break;
            case 6:
                stats.F = stats.F + 1;
                break;
        }

        stats.avg += result.rating;
    });
    stats.avg = stats.avg / results.length;

    console.log("Stats: ", stats);

    fs.writeFileSync(
        "./results.json",
        prettier.format(JSON.stringify(results), {
            semi: false,
            parser: "json",
            ...prettierConfig
        })
    );
};

executeFetches();
