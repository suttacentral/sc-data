Structural Data is the skeleton which the rest of the data fleshes out.

Some of these files are deprecated and should not be used for future development. We should remove them ASAP.

-  `sutta.json` is replaced by `name` files and `text_extra_info.json`as per https://github.com/suttacentral/suttacentral/issues/1771
- `grouping.json` and `pitaka.json` are replaced by `super-tree.json`
-  The `division` folder is replaced by `name` and `tree`.
- But `name` is now in `sc_bilara_data` do delete it from here.

The current files are as follows.

- `tree` files give the tree structure of the whole navigation. 
- `super-` files give the "superstructure", i.e. the higher-level structure as far as the individual text or division.
- `text_extra_info` gives supplementary information about texts.
- `super_extra_info` is the same, but for the `super-` files.
- `language.json` defines the language of each text or division.
- `sect.json` defines the sect (or better, "school") of Buddhism to which the text belongs.
- `shortcut.json` defines the navigation shortcuts.
- `child_range.json` defines the  acronym and suta range number of the children of the given ID. This is used as a navigation aid, it lets the user know what is contained.
- `super_root_lang.json` defines the **highest level** of the tree to which a language can be assigned. All children have that root language.
