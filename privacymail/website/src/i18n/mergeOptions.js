const fs = require("fs");

/**
 * This file was used to genereate the countries.json and sectors.json files.
 */
const de = JSON.parse(fs.readFileSync("./de_sectors.json"));
const en = JSON.parse(fs.readFileSync("./en_sectors.json"));

const mergedObject = [];

Object.keys(de).forEach(key => {
    mergedObject.push({
        key: key,
        de: de[key],
        en: en[key]
    });
});

fs.writeFileSync("./sectors.json", JSON.stringify(mergedObject));

//fs.writeFileSync(process.argv[2], JSON.stringify(result));
