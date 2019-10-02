- uid_expansion : Contains a mapping between uid components and the acronym and name. For example pli->Pli (short for Pali), but dn -> DN (abbreviation for Digha Nikaya)
- The other uid_expansion files are not used ATM, they contain exactly the same data as the main uid_expansion, just sorted into types. Sometimes I want to look at the details for a kind of thing and the full file doesn't let me do that. If this is a convenient form, maybe we should adopt it.
- pali_concord : key/value pairs for `ms` numbers (primary numberng system for Mahasangiti edition) vs. several other editions. From Mahasangiti.
- ms-sc-pts.json: keys the pts and sc numbers off the `ms` numbers
- sc-pts-undefined: a  few references that did not have corresponding `ms` numbers. They are verses. To be added tp bilara-data directly.
- all_pali_concordance.json: The King of Concordances. This merges `pali_concord` and `ms-sc-pts`. Many corrections were made, extra IDs added by hand, and the IDs brought to modern standards. IDs are keyed off the SC segment numbers. **Use this!**


The basic process:

```
const data = [{
  "ms1V_2": "cck1.1"},
  {"ms1V_2": "csp1ed1.1"},
  {"ms1V_2": "lv1.1"},
  {"ms1V_2": "lv87.2"},
  {"ms1V_2": "ndp1.3"},
  {"ms1V_2": "csp2ed1.1"},
  {"ms1V_2": "km1.1"},
  {"ms1V_2": "dr1.1"},
  {"ms1V_2": "bj1.2"},
  {"ms1V_2": "mc1.1"},
  {"ms1V_2": "pts3.1"},
  {"ms1V_2": "sya2ed1.1"},
  {"ms1V_2": "vri87.1"},
  }]

const result = data.reduce(function(r, e) {
  return Object.keys(e).forEach(function(k) {
    if(!r[k]) r[k] = [].concat(e[k])
    else r[k] = r[k].concat(e[k])
  }), r
}, {})

console.log(result)

{
  "ms1V_2": [
    "cck1.1",
    "csp1ed1.1",
    "lv1.1",
    "lv87.2",
    "ndp1.3",
    "csp2ed1.1",
    "km1.1",
    "dr1.1",
    "bj1.2",
    "mc1.1",
    "pts3.1",
    "sya2ed1.1",
    "vri87.1",
    "pli-tv-bu-vb-intro#2",
    "pts-vp-pli3.1",
    "msdiv1"
  ]}
```
