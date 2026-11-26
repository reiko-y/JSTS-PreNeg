否定接頭辞付きの語の抽出 (`src/dictionaries.py`) には、以下の 3 つの辞書データを使用します。各提供元から入手して、このディレクトリ直下に以下の構成で格納してください。

| 辞書                                           | 提供元                                              | `--dic`    |
| --------------------------------------------- | -------------------------------------------------- | -----------|
| EDR 電子化辞書 日本語単語辞書 (VERSION 2.0)       | [情報通信研究機構 (NICT)](https://www.nict.go.jp/)    | `jwd`      |
| 分類語彙表 増補改訂版 データベース (Ver.1.0)        | [国立国語研究所 (NINJAL)](https://www.ninjal.ac.jp/) | `bunruidb` |
| GSK2010-A 岩波国語辞典 第五版 タグ付きコーパス 2004 | [言語資源協会 (GSK)](https://www.gsk.or.jp/)         | `iwanami`  |

```
dictionaries/
├── J_WORD/
│   ├── jwd.dic
│   └── jwd.mat
├── 分類語彙表∹増補改訂版ー データベース 2004国立国語研究所/
│   └── bunruidb.txt
└── GSK2010-A-岩波国語辞典第五版2004/
    └── corpus/
        └── ... (*.dict)
```

なお、これらの辞書から抽出した結果 (`prefix-neg-words/extracted_from_dic/*.json`) はリポジトリに含まれているため、`src/dictionaries.py` を実行しない場合は辞書データは不要です。


The extraction of prefix-negated words (`src/dictionaries.py`) uses the following three dictionaries. Please obtain them from their providers and place them in this directory with the structure shown above.

| Dictionary                                                                         | Provider                                                                                                       | `--dic`    |
| ---------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- | ---------- |
| The EDR Electronic Dictionary, Japanese Word Dictionary (VERSION 2.0)              | [National Institute of Information and Communications Technology (NICT)](https://www.nict.go.jp/en/index.html) | `jwd`      |
| Word List by Semantic Principles, Revised and Enlarged Edition, Database (Ver.1.0) | [National Institute for Japanese Language and Linguistics (NINJAL)](https://www.ninjal.ac.jp/english/)         | `bunruidb` |
| GSK2010-A The Corpus of Iwanami Japanese Dictionary, Fifth Edition (2004)          | [Gengo-Shigen-Kyokai (GSK)](https://www.gsk.or.jp/en/)                                                         | `iwanami`  |

The words extracted from these dictionaries (`prefix-neg-words/extracted_from_dic/*.json`) are already included in this repository, so the dictionary data is not required unless you run `src/dictionaries.py`.
