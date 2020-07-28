# bilara-data

## variant

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
an10.99:6.2": "vaṅkakaṃ → vaṅkaṃ (si, pts-vp-pli1ed) | ciṅgulakaṃ → piṅgulikaṃ (sya-all); ciṅkulakaṃ (mr)"
```

> "The lemma 'vaṅkakaṃ' has a variant 'vaṅkaṃ' in the si and pts-vp-pli1ed editions. In addition, the lemma 'ciṅgulakaṃ' has the variant 'piṅgulikaṃ' in the sya-all edition, and another variant 'ciṅkulakaṃ' in the mr edition."

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