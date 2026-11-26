# JSTS-PreNeg

[[日本語](./README.md) | English]

## Abstract

This repository provides **JSTS-PreNeg**, a Japanese semantic textual similarity dataset focuses on negative prefixes.
JSTS-PreNeg is an extended version of **JSTS**, a Japanese semantic textual similarity dataset that is included in [JGLUE](https://aclanthology.org/2022.lrec-1.317/).

The JSTS-PreNeg dataset is stored in the [negative-prefix/data/jsts-preneg-v1.3/](./negative-prefix/data/jsts-preneg-v1.3/) and [double-negation/data/jsts-preneg-v1.3/](./double-negation/data/jsts-preneg-v1.3/) directories, and the source code used to construct JSTS-PreNeg is stored in the [negative-prefix/src](./negative-prefix/src/) and [double-negation/src](./double-negation/src/) directories, respectively.

## Table of Contents

- [JSTS-PreNeg](#jsts-preneg)
  - [Abstract](#abstract)
  - [Table of Contents](#table-of-contents)
  - [Dataset Statistics](#dataset-statistics)
  - [Source Code Description](#source-code-description)
    - [Setup](#setup)
    - [Run](#run)
  - [License](#license)

## Dataset Statistics

| Item                     | Count |
| ------------------------ | ----: |
| STS Instance             |   482 |
| Minimal Pair of Negation |   281 |

<!-- For the detail of "minimal pair of negation", please refer to [our paper](#paper). -->

## Source Code Description

We have released the source code used to construct JSTS-PreNeg.
By running the source code, you can reproduce the following process:

- Load the JSTS dataset and generate new sentence pairs $(s_1, s_2)$
  (corresponding to Step 1 in our paper).
- Load the results of manual annotation (Step 2) and generate the JSTS-PreNeg dataset.

### Setup

First, save this repository to your execution environment (e.g., fork and clone).
Then, set up the environment by following the steps below.
Please use an environment that supports Python 3.10 or later.

1. Download JSTS dataset

   Download `train-v1.3.json`, `valid-v1.3.json`, and `test-v1.3.json` from [the JSTS directory in JGLUE](https://github.com/yahoojapan/JGLUE/tree/main/datasets/jsts-v1.3), and place them directly under both the [negative-prefix/data/jsts-v1.3](./negative-prefix/data/jsts-v1.3/) and [double-negation/data/jsts-v1.3](./double-negation/data/jsts-v1.3/) directories.

2. Set up MeCab and UniDic

   This source code uses the morphological analyzer [MeCab](https://taku910.github.io/mecab/) and the morphological dictionary [UniDic](https://clrd.ninjal.ac.jp/unidic/).
   Install MeCab and UniDic by referring to
   [MeCab's official page](https://taku910.github.io/mecab/) and other resources.
   In addition, configure MeCab to use UniDic as its dictionary.
   If MeCab is set to use a different dictionary (e.g., IPA), the code may not work correctly.

3. Install required Python packages

   Install the required Python packages listed in [requirements.txt](./requirements.txt).
   If you are using pip, you can run:

   ```sh
   pip install -r requirements.txt
   ```

### Run

From the root directory of this repository, move to `negative-prefix` or `double-negation` (`cd negative-prefix` or `cd double-negation`) and execute run.sh.
Make sure to use Python 3.10 or later.

## License

The JSTS-PreNeg dataset and source code are distributed under the following licenses:

- JSTS-PreNeg dataset: [CC-BY-SA-4.0](https://creativecommons.org/licenses/by-sa/4.0/)
- source code: [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0)

<!-- ## Paper

If you use this repository in your work, please reference the following paper.

```bibtex

``` -->
