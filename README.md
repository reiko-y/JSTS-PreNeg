# JSTS-PreNeg

[日本語 | [English](./README_en.md)]

## 概要

接頭辞の否定理解能力を評価するための日本語意味的類似度計算データセット **JSTS-PreNeg** の公開用リポジトリです。
JSTS-PreNeg は、[JGLUE](https://www.jstage.jst.go.jp/article/jnlp/30/1/30_63/_article/-char/ja)
に含まれる言語推論データセット **JSTS** を拡張して作成しました。

JSTS-PreNeg データセットは [negative-prefix/data/jsts-preneg-v1.3/](./negative-prefix/data/jsts-preneg-v1.3/) および [double-negation/data/jsts-preneg-v1.3/](./double-negation/data/jsts-preneg-v1.3/) ディレクトリに、
JSTS-PreNeg の作成に使用したソースコードはそれぞれ [negative-prefix/src](./negative-prefix/src/) および [double-negation/src](./double-negation/src/) ディレクトリに格納しています。

## 目次

- [JSTS-PreNeg](#jsts-preneg)
  - [概要](#概要)
  - [目次](#目次)
  - [データセットの統計情報](#データセットの統計情報)
  - [ソースコードの説明](#ソースコードの説明)
    - [環境構築](#環境構築)
    - [実行方法](#実行方法)
  - [ライセンス](#ライセンス)

## データセットの統計情報

| 項目              | 件数 |
| ---------------- | --: |
| STS インスタンス   | 482 |
| 否定のミニマルペア  | 281 |

<!-- 「否定のミニマルペア」に関する詳細は、[論文](#論文情報)を参照してください。 -->

## ソースコードの説明

JSTS-PreNeg の構築に利用したソースコードを公開しています。
ソースコードを実行することで、以下の動作を再現できます。

- JSTS のデータを読み込み、新たな文の組 $(s_1, s_2)$ を作成する
  (論文の構築手法における手順 1)
- 人手アノテーション (手順 2) の結果を読み込み、JSTS-PreNeg データセットを作成する

### 環境構築

このリポジトリを実行環境に保存 (fork + clone など) した上で、
以下の手順で環境構築を行ってください。
python 3.10 以降を実行できる環境を使用してください。

1. JSTS データセットのダウンロード

   [JGLUE のリポジトリにおける JSTS 格納ディレクトリ](https://github.com/yahoojapan/JGLUE/tree/main/datasets/jsts-v1.3) から
   `train-v1.3.json`, `valid-v1.3.json`, 及び `test-v1.3.json` をダウンロードし、
   本リポジトリの [negative-prefix/data/jsts-v1.3](./negative-prefix/data/jsts-v1.3/) ディレクトリおよび [double-negation/data/jsts-v1.3](./double-negation/data/jsts-v1.3/) ディレクトリ直下に格納してください。

2. MeCab 及び UniDic の準備

   本ソースコードでは、形態素解析器 [MeCab](https://taku910.github.io/mecab/) 及び形態素解析辞書 [UniDic](https://clrd.ninjal.ac.jp/unidic/) を使用します。
   [MeCab の公式ページ](https://taku910.github.io/mecab/) などを参照して、実行環境に MeCab 及び UniDic をインストールしてください。
   さらに、MeCab の解析用辞書を UniDic に設定してください。
   UniDic 以外の辞書 (IPA など) を利用する設定になっている場合、ソースコードが正しく動作しないので注意してください。

3. 必要な python パッケージのインストール

   [requirements.txt](./requirements.txt) を参照して、
   必要な python パッケージを実行環境にインストールしてください。
   pip を使用する場合、以下のコマンドで一括インストールできます。

   ```sh
   pip install -r requirements.txt
   ```

### 実行方法

本リポジトリのルートディレクトリから`cd negative-prefix` または `cd double-negation` で移動し run.sh を実行することにより、処理を実行することができます。
python 3.10 以降のバージョンを利用してください。

## ライセンス

JSTS-PreNeg データセットとソースコードは、それぞれ以下のライセンスで配布します。

- JSTS-PreNeg データセット: [CC-BY-SA-4.0](https://creativecommons.org/licenses/by-sa/4.0/)
- ソースコード: [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0)

<!-- ## 論文情報

本リポジトリを利用する場合、以下の論文を引用してください。

```bibtex

``` -->
