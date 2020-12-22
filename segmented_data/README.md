# bilara-data

This repository contains the published and unpublished translations, root texts, and other data from the Bilara translation app.

- The `published` branch is the main branch and contains finished translations and other texts. **Use `published` branch for any form of publishing**. In software terms it can be considered to be “stable”. 
- The `unpublished` branch contains translations which are still in progress. **Do not use material from `unpublished` except for internal SuttaCentral uses.** In software terms it can be considered to be the “develop” branch. There should be no data integrity issues but there are no guarantees about the content. 

## Warning

Pull Requests such as from a fork should not be made against published branch. Instead pull requests should be made against the unpublished branch.

For manual publication workflow within this repository, please refer to https://github.com/suttacentral/bilara-data/wiki/Manual-publication-workflow

## How it works

Bilara consumes `json` objects where:

- the key is a unique segment identifier
- the value is a string corresponding to the identifier.

The value may be root text, translation, comments, variant readings, markup and so on. Each different kind of data is contained in a separate directory.

Let us look at a simple example. Here is a text with in the /root/ directory with the segment ID `mn1:1.1`.

```
"mn1:1.1": "Evaṁ me sutaṁ—",
```
The translation/en directory contains the same ID with a translated string:

```
"mn1:1.1": "So have I heard.",
```

There might be a comment on this in /comment/:

```
"mn1:1.1": "Traditionally attributed to the Buddha’s closest disciple, Ānanda.",
```
And some markup in /html/:

```
"mn1:1.1": "<p><span class='evam'>{}</span>",
```

Note that `{}` is used as placeholder for text in the /html files. By convention, use single quotes in `html` to avoid confusion with JSON.

Bilara texts are kept in files where one file is approximately one text. However the files are just for convenience, and may be changed by an application. For example, a very long text might be split into multiple HTML files for display on the web. However, the segment IDs should remain immutable.

## Publication

Publication details are recorded canonically in `_publication.json`. Publications are scoped by collection such as `mn`, `dhp`, etc. Each “publication” thus corresponds roughly with a “book”. This doesn’t mean all texts in the work must be finished, it is just for convenience.

A record in `_publication.json` is required for every translation project. To get started, it requires at minimum:

- `publication_number`: a simple incremented ID.
 - `root_lang`
 - `translation_lang`
 - `author_uid` — must be unique in SC, usually may be github handle.
- `author_name` — full name under which work will be published.
- `author_github_handle` — prefer something like real name.
- `text_uid` — select one text such as mn, dn, etc. to start.
- `"is_published": "false"`
- `license` must be set to CC0. Note that all translations supported by SuttaCentral must use CC0 licence.

If the translation is by a team, there should be a team name that is independent of the author names. Use eg. `pt-team` by default. It can be changed later. Collaborator details must be added as per author details above.

Other details can be added later.

Once a project is ready to be published, all relevant fields should be filled in, and set `"is_published": "true"`.

The text will be switched to the `published` branch, signfying that it is ready to be consumed by apps.

## Inline markup

Text inside segment strings should avoid using markup. A subset of markdown may be used, with slightly specialized meanings:

- `*asterisks*` mean emphasis (= `<em>`), usually rendered as italics.
- `_underscores_` are not synonyms for asterisk, but are used when quoting a word from the root text in the translation. (= `<i lang='pli' translate='no'>`)
- `**double asterisk**` may be used to signify strong emphasis i.e. bold, but I wouldn’t encourage it! (= `<strong>`)
- `#123` indicates a number used for counting sections. These are inherited from the Mahasangiti edition. Typically they serve to clarify the structure of complex sections. (= `<span class='counter'>123</span>`)

## Bilara i/o

This is a utility for importing and exporting data from Bilara. It allows you to pull together the data for the same text from different directories. It is a very flexible tool, but we envisage two main use-cases:

1. Internal SC work, especially changing segments in bilara-data
2. Consumption of `bilara-data` in external apps

The basic usage is to export a text or range of texts as a spreadsheet. The data can then be viewed or manipulated in the spreadsheet, and the result imported back into `bilara-data`. 

A typical use case would be if we discover that a text has an extra unwanted segment break, we can combine two segments into one, delete the old segment, and re-import it. Changing this in the raw json files is tricky, as you have to keep track of all the different files of that particular text, and re-increment the segment numbering.

Bilara i/o uses [Pyexcel](http://www.pyexcel.org/) under the hood, so data can be imported and exported to [any format supported by pyexcel](http://docs.pyexcel.org/en/latest/design.html#data-format). However we have only extensively tested it with `.ods` spreadsheets.

### Use bilara i/o

Go to the .scripts folder. Change the python version to 3.7.2. (Other versions may work if you have a different version installed.) Run something like:

```
pip3 install -r requirements.txt
```

Ready to go, let’s export dn1 as a Libreoffice spreadsheet!

```
./sheet_export.py dn1 dn1.ods
```

Edit it, save, and run:

```
 ./sheet_import.py dn1.ods
 ```

Et voila, your changes appear in the bilara data file.

You can easily do something like this, too:

```
./sheet_export.py dn dn.tsv --include root, translation+en
```

“Export the whole of DN as a tsv file, including only the root text and English translation”.

## Some notes on SC-specific data

### Variant readings

The structure of the variant readings entries is as follows.

Here is a typical simple entry.

```
"an10.96:1.3": "Tapodāya → tapode (bj, mr)",
```

Which means: 

> "On this segment, the root text (lemma) 'Tapodāya' has a variant 'tapode' indicated by an arrow, which is found in the bj and mr editions."

The details for each edition is found in `uid_expansion`.

More generally:

```
"segment": "lemma → variant (edition)"
```

Editions are separated by commas, as above. Where the same lemma has multiple variants in different editions, semi-colon is used.

```
"an10.98:1.10": "abhikkantapaṭikkante → abhikkante paṭikkante (bj); abhikkantapaṭikkanto (mr)"
```

> "The lemma 'abhikkantapaṭikkante' has a variant 'abhikkante paṭikkante' in the bj edition, and another variant 'abhikkantapaṭikkanto' in the mr edition."


When multiple lemmas have variants on the same segment, pipe `|` is used as separator.

```
an10.99:6.2": "vaṅkakaṁ → vaṅkaṁ (si, pts-vp-pli1ed) | ciṅgulakaṁ → piṅgulikaṁ (sya-all); ciṅkulakaṁ (mr)"
```

> "The lemma 'vaṅkakaṁ' has a variant 'vaṅkaṁ' in the si and pts-vp-pli1ed editions. In addition, the lemma 'ciṅgulakaṁ' has the variant 'piṅgulikaṁ' in the sya-all edition, and another variant 'ciṅkulakaṁ' in the mr edition."

The use of empty brackets indicates a place in the mahasangiti edition where a passage was not found, but was present in other editions.

```
an2.49:1.6": "() → (visamattā bhikkhave parisāya adhammakammāni pavattanti … vinayakammāni na dippanti.) (bj, sya-all, pts-vp-pli1ed)",
```

> "In the place marked by (), the passage 'visamattā bhikkhave parisāya adhammakammāni pavattanti … vinayakammāni na dippanti.' is found in the bj, sya-all, and pts-vp-pli1ed editions."

Occasionally the variants offer a short explanation in Pali as to an unusual textual situation.

```
an11.6:1.1": "etthantare pāṭho si, sya-all, km, pts-vp-pli1ed potthakesu na
```

> "The indicated passage is not found in the si, sya-all, km, and pts-vp-pli1ed editions."

### References

The reference files contain detailed references to over a dozen editions of the Pali canon. These were originally collated by the Dhamma Society for their Mahsaṅgīti edition, and have been supplemented by SuttaCentral.

The full forms of the abbreviations may be found in `pali_edition.json`.
