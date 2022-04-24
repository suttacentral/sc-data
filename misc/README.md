

## Current

- `pali_reference_edition`: use for details of Pali editions. Similar to `root_edition`, but updated for the Pali, and `root_edition` adds non-Pali texts.
- `uid_expansion_edition`, `uid_expansion_language`, `uid_expansion_school`

## Deprecated

The following files are deprecated and should not be used. They are only kept to avoid breaking legacy uses. If there are no legacy uses, delete them.

- `uid_expansion`: old expansion for uid = acronym = name.

Current:

- `uid` --> `acronym` is in `sc-data/structure/super_extra_info.json`
- "names" are in the `name` files, the top level is `/sc-data/sc_bilara_data/root/misc/site/name/`

## Removed

- `an_cck_fix` 
- `pali_concord`: Essentially a data dump, it's really messy in the original data too.
- `all_pali_concordance`: info now in bilara-data references.
- `ms-sc-pts` : info now in bilara-data references.
- `uncorrected_pali_concord`
- `uid_expansion_text`: super_extra_info, and super-name.
- `uid_expansion_misc` trivial and unused

