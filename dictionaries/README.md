# README.md

The dictionaries are divided into two types.

- Simple dictionaries use structured JSON containing strings.
- Complex dictionaries use unstructured JSON containing text structured with HTML.

Note that in one case (`pli2id_cped.json`) the simple dictionary contains plain HTML inline markup (`<b>`, `<i>`). If this causes problems, strip it out. 

JSON structure for simple dictionaries may contain the following fields:

- `entry`: the head word to be defined
- `grammar`: grammatical analyis of entry, especially for Indic languages
- `pronunciation`: Romanized word to aid pronunciation, especially for Chinese
- `definition`: definition of word. Note that in some cases, grammatical information is not cleanly separated so is included in the definition.
- `xr`: cross-reference, i.e. related terms, individual members of a compound, etc.

Please note:

-  `grammar`, `definition`, and `xr` may be an array.
- `grammar` replaces `case` in the deprecated files. This has also been changed in /complex/pli2en_pts.

Dictionaries are used in two places.

- Lookup tool uses simple dictionaries
- Search results use both simple and complex

The file names for the dictionaries are eg. `pli2en_ncped.json` where

 - `pli` = source language ISO
 - `en` = target language ISO
 - `ncped` = name of dictionary

## Deprecated

Everything that is not in the folders /simple, /complex, and /utilities is deprecated. Do not use it, and delete it as soon as possible.