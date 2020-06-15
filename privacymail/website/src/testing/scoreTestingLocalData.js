const fs = require("fs");
const prettier = require("prettier");
const prettierConfig = require("../../package.json").prettier;
const fetch = require("node-fetch");

const executeFetches = async () => {
    let results = JSON.parse(fs.readFileSync("./resultsWithPenalty.json"));

    const stats = {
        A: 0,
        B: 0,
        C: 0,
        D: 0,
        E: 0,
        F: 0,
        avg: 0
    };
    const penalty = {
        avg: 0
    };

    //results = results.filter(result => result.count_mails >= 1);

    results.forEach(result => {
        const oldResult = result;
        result = result.rating;
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

        const roundedPenalty = Math.round(result.penalty * 100) / 100;
        penalty[roundedPenalty] = penalty[roundedPenalty] ? penalty[roundedPenalty] + 1 : 1;
        penalty.avg += result.penalty;

        let hasOnView = 0;
        let hasOnClick = 0;

        /*oldResult.third_parties.forEach(trd => {
            if (trd.embed_as.includes("ONVIEW")) {
                hasOnView++;
            }
            if (trd.embed_as.includes("ONCLICK")) {
                hasOnClick++;
            }
        });

        if (hasOnView === 0 && hasOnClick >= 2) {
            console.log(oldResult.service.name);
        }*/
        if (oldResult.count_mails === 0 && oldResult.rating.rating > 1) {
            console.log(oldResult.service.name);
        }
    });
    stats.avg = stats.avg / results.length;
    penalty.avg = penalty.avg / results.length;

    console.log("Stats: ", stats);
    //console.log("Penalty: ", penalty);
};

executeFetches();
