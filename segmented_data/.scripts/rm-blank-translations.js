#!/usr/bin/env node

const path = require("path");
const fs = require("fs");

function process_dir(dname) {
    fs.readdirSync(dname, {withFileTypes:true}).forEach(de => {
        try {
            var p = path.join(dname, de.name);
            if (de.isDirectory()) {
                process_dir(p);
            } else if (de.name.endsWith('.json')) {
                var json = JSON.parse(fs.readFileSync(p));
                var textCount = Object.keys(json).reduce((a,k) => {
                    return a + json[k].trim().length;
                }, 0);
                if (textCount === 0) {
                    console.log(`Removing empty json`, p);
                    fs.unlinkSync(p);
                }
            }
        } catch(e) {
            console.error(e.stack);
        }
    });
}

process_dir("translation/de/sabbamitta");
