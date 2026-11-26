# Double Negation with a Negative Prefix

[[日本語](./README.md) | English]

## Abstract

This directory contains the subset of the JSTS-PreNeg dataset that focuses on double negation with a negative prefix.
The dataset is stored in the [data/jsts-preneg-v1.3/](./data/jsts-preneg-v1.3/) directory, and the source code used to construct it is stored in the [src](./src/) directory.

## Table of Contents

- [Double Negation with a Negative Prefix](#double-negation-with-a-negative-prefix)
  - [Abstract](#abstract)
  - [Table of Contents](#table-of-contents)
  - [Dataset Statistics](#dataset-statistics)
  - [Dataset Description](#dataset-description)

## Dataset Statistics

| Item                     | Count |
| ------------------------ | ----: |
| STS Instance             |   92 |
| Minimal Pair of Negation |   54 |

## Dataset Description

The dataset is provided in the JSON format,
with each instance structured as shown below.

```json
{
  "id": 5,
  "jsts_sentence_pair_id": 606,
  "pair_id_in_group": 1,
  "type": "s1_neg",
  "sentence1": {
    "sentence": "グラスに不透明でない液体が入っています。",
    "neg": {
      "neg_id_in_jsts_sentence": 0,
      "neg_prefix": "不"
    }
  },
  "sentence2": {
    "sentence": "お皿に透明な液体が入っています。",
    "neg": null
  },
  "gold_label": "3",
  "annotator_labels": {
    "5": 0,
    "4": 1,
    "3": 2,
    "2": 0,
    "1": 0,
    "0": 0
  }
}
```

The details of the keys and values are as follows:

- `id` (integer): instance id within the negative-prefix subset of JSTS-PreNeg
- `jsts_sentence_pair_id` (integer):
  _sentence_pair_id_ of the corresponding instance in JSTS that was used for augmentation
- `pair_id_in_group`(integer):
  id within the group of JSTS-PreNeg instances created from the same JSTS instance by adding negative prefixes.
  If a JSTS instance $i$ is augmented into a set of JSTS-PreNeg instances $`I^{\prime}=\{i^{\prime}_{1}, i^{\prime}_{2}, i^{\prime}_{3}, \dots, i^{\prime}_{n} \}`$, then the index $k$ of $i^{\prime}_{k}$ corresponds to _pair_id_in_group_.
  The original JSTS instance used for augmentation has _pair_id_in_group_ set to 0.
- `type` (string):
  type of the sentence pair based on negation presence.
  Possible values:
  - `s1_neg`: only the sentence1 contains negation
  - `s2_neg`: only the sentence2 contains negation
  - `s1_neg_s2_neg`: both the sentence1 and sentence2 contain negation
  - `original`: original JSTS instance (neither the sentence1 nor sentence2 contains negation)
- `sentence1` (object: explained below): sentence1
- `sentence2` (object: explained below): sentence2
- `gold_label` (string): ground-truth similarity score, with possible values `5`, `4`, `3`, `2`, `1`, or `0`
- `annotator_labels` (object):
  annotation results provided by three human annotators

The format of the values for `sentence1` and `sentence2` is as follows:

- `sentence` (string): plain text of the sentence
- `neg` (object | null):
  information about negation, if present in the sentence.
  If the sentence does not contain negation, the value is null.
  If the sentence contains negation, the value is the object with the following fields:
  - `neg_id_in_jsts_sentence` (integer):
    id within the set of sentences derived from a single JSTS sentence.
    Given a JSTS sentence $s$ (either sentence1 or sentence2) augmented into a set $`S^{\prime}=\{s^{\prime}_{1}, s^{\prime}_{2}, s^{\prime}_{3}, \dots, s^{\prime}_{n} \}`$, the index $k$ of $s^{\prime}_{k}$ corresponds to _neg_id_in_jsts_sentence_.
  - `neg_prefix` (string): negative prefix added during augmentation, with possible values `非`, `不`, `無`, or `未`
