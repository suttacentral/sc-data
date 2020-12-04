Structural Data is the skeleton which the rest of the data fleshes out.

Some of these files are deprecated and should not be used for future development.

-  `sutta.json` is replaced by `name` files and `text_extra_info.json`as per https://github.com/suttacentral/suttacentral/issues/1771
- `grouping.json` and `pitaka.json` are replaced by `super-tree.json`
-  The `division` folder is replaced by `name` and `tree`.

The current files are as follows.

- `tree` files give the tree structure of the whole navigation. 
- `name` files list the titles.
- `super-` files give the "superstructure", i.e. the higher-level structure as far as the individual text or division.
- `text_extra_info` gives supplementary information about texts.
- `super_extra_info` is the same, but for the `super-` files.
- `language.json` defines the language of each text or division.
- `sect.json` defines the sect (or better, "school") of Buddhism to which the text belongs.
- `shortcut.json` defines the navigation shortcuts.
