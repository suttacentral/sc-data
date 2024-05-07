const fs = require('fs');

const dpd_ebts = JSON.parse(fs.readFileSync('./dpd_ebts.json', 'utf8'));
const dpd_i2h = JSON.parse(fs.readFileSync('./dpd_i2h.json', 'utf8'));
const dpd_deconstructor = JSON.parse(fs.readFileSync('./dpd_deconstructor.json', 'utf8'));


const deconstructorReformated = Object.entries(dpd_deconstructor).map(([key, value]) => ({
    entry: key,
    defintion: [value]
}));

const dpd_master = Object.entries(dpd_i2h).map(([entry, subEntries]) => ({
    entry: entry,
    definition: subEntries.map(subEntry => dpd_ebts[subEntry])
})).concat(deconstructorReformated).sort((a, b) => {
    const defA = a.entry
    const defB = b.entry
    if (defA < defB) {
        return -1;
    }
    if (defA > defB) {
        return 1;
    }
    return 0;
});;

fs.writeFileSync('../dictionaries/simple/en/pli2en_dpd.json', JSON.stringify(dpd_master, null, 2), 'utf8');

