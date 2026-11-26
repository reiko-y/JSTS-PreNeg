# Double Negation with a Negative Prefix

[日本語 | [English](./README_en.md)]

## 概要

JSTS-PreNeg データセットのうち、接頭辞の否定要素を含む二重否定に着目したものを格納しています。
データセットは [data/jsts-preneg-v1.3/](./data/jsts-preneg-v1.3/) ディレクトリに、
作成に使用したソースコードは [src](./src/) ディレクトリに格納しています。

## 目次

- [Double Negation with a Negative Prefix](#double-negation-with-a-negative-prefix)
  - [概要](#概要)
  - [目次](#目次)
  - [データセットの統計情報](#データセットの統計情報)
  - [データセットの説明](#データセットの説明)

## データセットの統計情報

| 項目              | 件数 |
| ---------------- | --: |
| STS インスタンス   |  92 |
| 否定のミニマルペア  |  54 |

## データセットの説明

データセットは JSON 形式です。
各インスタンスは、以下のようなフォーマットで表現されます。

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

key, value (値) の詳細は以下の通りです。

- `id` (integer): JSTS-PreNeg のうち、接頭辞の否定要素を含む二重否定に着目したものにおける id
- `jsts_sentence_pair_id` (integer):
  拡張対象とした JSTS のインスタンスにおける _sentence_pair_id_
- `pair_id_in_group`(integer):
  同一の JSTS インスタンスから接頭辞の否定要素を含む二重否定に関して拡張して作成した JSTS-PreNeg インスタンスの集合 (グループ) における id 。
  ある JSTS インスタンス $i$ から作成した JSTS-PreNeg インスタンスの集合 $`I^{\prime}=\{i^{\prime}_{1}, i^{\prime}_{2}, i^{\prime}_{3}, \dots i^{\prime}_{n} \}`$ における $i^{\prime}_{k}$ の添字 $k$ が _pair_id_in_group_ に相当する。
  拡張対象とした JSTS のインスタンスの _pair_id_in_group_ は 0 としている。
- `type` (string):
  文1と文2の組み合わせに関する種類。
  値は以下のいずれか 1 つ。
  - `s1_neg`: 文1にのみ否定要素を含む
  - `s2_neg`: 文2にのみ否定要素を含む
  - `s1_neg_s2_neg`: 文1と文2の両方に否定要素を含む
  - `original`: 拡張対象とした JSTS のインスタンス (文1と2文のいずれにも否定要素を含まない)
- `sentence1` (object: 以下で説明): 文1
- `sentence2` (object: 以下で説明): 文2
- `gold_label` (string):
  正解の類似度。値は`5`, `4`, `3`, `2`, `1`, `0`のいずれか 1 つ。
- `annotator_labels` (object):
  3 人の作業者による人手アノテーションの結果

`sentence1` 及び `sentence2` の値のフォーマットは以下の通りです。

- `sentence` (string): 平文
- `neg` (object | null):
  文に含まれる否定の情報。
  否定を含まない文の値は null 。
  否定を含む文における値は以下の形式。
  - `neg_id_in_jsts_sentence` (integer):
    1 つの JSTS の文から作成した否定を含む文の集合における id 。
    ある JSTS の文 (文1と文2のいずれか) $s$ から作成した 否定を含む文の集合 $`S^{\prime}=\{s^{\prime}_{1}, s^{\prime}_{2}, s^{\prime}_{3}, \dots s^{\prime}_{n} \}`$ における $s^{\prime}_{k}$ の添字 $k$ が _neg_id_in_jsts_sentence_ に相当する。
  - `neg_prefix` (string): 拡張において付与した接頭辞の否定要素。値は`非`, `不`, `無`, `未`のいずれか 1 つ。
