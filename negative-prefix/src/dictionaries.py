from pathlib import Path
from itertools import product
import xml.etree.ElementTree as ET

from tap import Tap
from tqdm import tqdm

import literals as L
import paths as P
import utils as U


class DICTIONARY:
    """
    Base class for dictionaries
    """

    def __init__(self) -> None:
        self.records: list = []
        self.headwords: set[str] = set()

    def extract_prefix_neg_words(self) -> dict[str, set[str]]:
        """
        Extract prefix-negated words (implemented in subclasses)
        """
        raise NotImplementedError


class JWD_RECORD:
    """
    A single record of 日本語単語辞書 (the EDR Japanese Word Dictionary VERSION 2.0)
    """

    def __init__(self, record: str) -> None:
        assert len(record.split(sep="\t")) == 19
        self.record_number: str = record.split(sep="\t")[0]
        # Split the entry into the headword written with its inflectional ending and its reading
        self.headword_notation: str = record.split(sep="\t")[1].split(sep="[")[
            0
        ]
        self.reading_of_headword: str = record.split(sep="\t")[1].split(
            sep="["
        )[1][:-1]
        self.invariable_portion_and_pair_of_adjacency: str = record.split(
            sep="\t"
        )[2]
        self.kana_notation: str = record.split(sep="\t")[3]
        self.pronunciation: str = record.split(sep="\t")[4]
        self.pos: str = record.split(sep="\t")[5]
        self.syntactic_tree: str = record.split(sep="\t")[6]
        self.conjugational_info: str = record.split(sep="\t")[7]
        self.surface_case_info: str = record.split(sep="\t")[8]
        self.aspect_info: str = record.split(sep="\t")[9]
        self.func_word_info: str = record.split(sep="\t")[10]
        self.concept_id: str = record.split(sep="\t")[11]
        self.en_headconcept: str = record.split(sep="\t")[12]
        self.ja_headconcept: str = record.split(sep="\t")[13]
        self.en_concept_explication: str = record.split(sep="\t")[14]
        self.ja_concept_explication: str = record.split(sep="\t")[15]
        self.usage: str = record.split(sep="\t")[16]
        self.freq: str = record.split(sep="\t")[17]
        self.management_info: str = record.split(sep="\t")[18]


class JWD_DIC(DICTIONARY):
    """
    日本語単語辞書（the EDR Japanese Word Dictionary VERSION 2.0）
    """

    def __init__(self) -> None:
        self.dic_path: Path = Path("dictionaries/J_WORD/jwd.dic")
        self.mat_path: Path = Path("dictionaries/J_WORD/jwd.mat")
        # All records
        self.records: list[JWD_RECORD] = []
        # Set of headword spellings
        self.headwords: set[str] = set()

        with open(
            file=self.dic_path, mode="r", encoding="euc_jp", errors="replace"
        ) as fp:
            # Skip the first line
            next(fp)

            for line in fp:
                record = JWD_RECORD(record=line)
                self.records.append(record)
                self.headwords.add(record.headword_notation)

    def extract_prefix_neg_words(self) -> dict[str, set[str]]:
        """
        Extract prefix-negated words
        """
        # Store results as {prefix: {set of headwords}}
        results: dict[str, set[str]] = {
            prefix: set() for prefix in L.PREFIXES.__args__
        }

        for record in tqdm(self.records):
            # Process each prefix
            for prefix in L.PREFIXES.__args__:
                # If the word starts with the prefix and the word without the prefix exists as a headword
                if (
                    record.headword_notation.startswith(prefix)
                    and len(record.headword_notation) >= len(prefix) + 2
                    and record.headword_notation[len(prefix) :]
                    in self.headwords
                ):
                    results[prefix].add(
                        record.headword_notation[len(prefix) :]
                    )

        return results


class BUNRUIDB_RECORD:
    """
    A single record of 分類語彙表-増補改訂版-　データベース　Ver1.0 (Word list by semantic principles - revised and enlarged edition database (Version 1.0))
    """

    def __init__(self, record: str) -> None:
        assert len(record.split(sep=",")) == 15
        # Fields that make up a record
        self.record_number: str = record.split(sep=",")[0]
        self.headword_number: str = record.split(sep=",")[1]
        self.record_type: str = record.split(sep=",")[2]
        self.category: str = record.split(sep=",")[3]
        self.subcategory: str = record.split(sep=",")[4]
        self.komoku2: str = record.split(sep=",")[5]
        self.komoku1: str = record.split(sep=",")[6]
        self.komoku1_number: str = record.split(sep=",")[7]
        self.paragraph_number: str = record.split(sep=",")[8]
        self.subparagraph_number: str = record.split(sep=",")[9]
        self.word_number: str = record.split(sep=",")[10]
        self.headword: str = record.split(sep=",")[11]
        self.headword_body: str = record.split(sep=",")[12]
        self.kana_notation: str = record.split(sep=",")[13]
        self.reverse_reading: str = record.split(sep=",")[14]


class BUNRUIDB_DIC(DICTIONARY):
    """
    分類語彙表-増補改訂版-　データベース　Ver1.0 (Word list by semantic principles - revised and enlarged edition database (Version 1.0))
    """

    def __init__(self) -> None:
        self.dic_path: Path = Path(
            "dictionaries/分類語彙表∹増補改訂版ー データベース 2004国立国語研究所/bunruidb.txt"
        )
        # All records
        self.records: list[BUNRUIDB_RECORD] = []
        # Set of headword spellings
        self.headwords: set[str] = set()

        with open(
            file=self.dic_path,
            mode="r",
            encoding="shift_jis",
            errors="replace",
        ) as fp:
            for line in fp:
                record = BUNRUIDB_RECORD(record=line)
                self.records.append(record)
                self.headwords.add(record.headword_body)

    def extract_prefix_neg_words(self) -> dict[str, set[str]]:
        """
        Extract prefix-negated words
        """
        # Store results as {prefix: {set of headwords}}
        results: dict[str, set[str]] = {
            prefix: set() for prefix in L.PREFIXES.__args__
        }

        for record in tqdm(self.records):
            # Process each prefix
            for prefix in L.PREFIXES.__args__:
                # If the word starts with the prefix and the word without the prefix exists as a headword
                if (
                    record.headword_body.startswith(prefix)
                    and len(record.headword_body) >= len(prefix) + 2
                    and record.headword_body[len(prefix) :] in self.headwords
                ):
                    results[prefix].add(record.headword_body[len(prefix) :])

        return results


class IWANAMI_RECORD:
    """
    A single record of GSK2010-A-岩波国語辞典第五版2004 (the Corpus of Iwanami Japanese Dictionary Fifth Edition)
    """

    def __init__(self, file_path: Path) -> None:
        self.file_path: Path = file_path
        # File name (without extension)
        self.record_number: str = file_path.stem

        # Parse the XML record and extract each field
        with open(
            file=file_path, mode="r", encoding="shift_jis", errors="replace"
        ) as fp:
            xml: str = fp.read()

        root: ET.Element = ET.fromstring(text=xml)
        assert root.tag == "gda"

        entry: ET.Element | None = root.find(path="entry")
        if entry is None:
            raise ValueError(f"entry tag is not found: {file_path}")

        self.entry: ET.Element = entry

        # Attributes of the entry tag
        self.entry_attributes: dict[str, str] = dict(self.entry.attrib)
        self.entry_id: str | None = self.entry.attrib.get("id")
        self.entry_notation: str | None = self.entry.attrib.get("entry")
        self.entry_annotator: str | None = self.entry.attrib.get("resp")
        self.entry_type: str | None = self.entry.attrib.get("type")
        self.is_kanji_entry: bool = self.entry_type == "k"

        # Child elements shared by general, derived-word, and kanji entries
        self.headword: str = self._get_required_text(tag="hd")
        self.orthography: str | None = self._get_text(tag="orth")
        self.senses: list[ET.Element] = self.entry.findall(path="sense")
        self.sense_texts: list[str] = [
            self._element_text(element=sense) for sense in self.senses
        ]

        # Child elements of general and derived-word entries
        self.historical_kana_notation: str | None = self._get_text(tag="hst")
        self.pos: str | None = self._get_text(tag="pos")

        # Child elements of kanji entries
        self.old_orthography: str | None = self._get_text(tag="old")
        self.pronunciations_element: ET.Element | None = self.entry.find(
            path="prns"
        )
        self.common_pronunciations: list[str] = self._get_texts_in_prns(
            tag="tprn"
        )
        self.other_pronunciations: list[str] = self._get_texts_in_prns(
            tag="prn"
        )
        self.direct_common_pronunciations: list[str] = self._get_direct_texts(
            tag="tprn"
        )
        self.direct_other_pronunciations: list[str] = self._get_direct_texts(
            tag="prn"
        )
        self.pronunciations: list[str] = (
            self.common_pronunciations
            + self.other_pronunciations
            + self.direct_common_pronunciations
            + self.direct_other_pronunciations
        )

        # Also keep information directly under entry that is not listed in the manual
        known_tags: set[str] = {
            "hd",
            "hst",
            "orth",
            "pos",
            "sense",
            "prns",
            "tprn",
            "prn",
            "old",
        }
        self.other_elements: dict[str, list[ET.Element]] = {}
        self.other_element_texts: dict[str, list[str]] = {}
        for child in self.entry:
            if child.tag in known_tags:
                continue
            self.other_elements.setdefault(child.tag, []).append(child)
            self.other_element_texts.setdefault(child.tag, []).append(
                self._element_text(child)
            )

        # For prefix-negated word extraction, prefer the standard spelling if present; otherwise use the headword
        self.headwords: set[str] = self._normalize_headwords(
            headword=self.orthography or self.headword
        )

    def _get_required_text(self, tag: str) -> str:
        text: str | None = self._get_text(tag=tag)
        if text is None:
            raise ValueError(f"{tag} tag is not found: {self.file_path}")
        return text

    def _get_text(self, tag: str) -> str | None:
        element: ET.Element | None = self.entry.find(path=tag)
        if element is None:
            return None

        text: str = self._element_text(element=element)
        return text if text else None

    def _get_direct_texts(self, tag: str) -> list[str]:
        return [
            text
            for text in (
                self._element_text(element)
                for element in self.entry.findall(path=tag)
            )
            if text
        ]

    def _get_texts_in_prns(self, tag: str) -> list[str]:
        if self.pronunciations_element is None:
            return []

        return [
            text
            for text in (
                self._element_text(element)
                for element in self.pronunciations_element.findall(path=tag)
            )
            if text
        ]

    def _element_text(self, element: ET.Element) -> str:
        return "".join(element.itertext()).strip()

    def _normalize_headwords(self, headword: str) -> set[str]:
        headwords: set[str] = set()

        for candidate in headword.split(sep="／"):
            normalized: str = (
                candidate.strip()
                .replace("=", "")
                .replace("△", "")
                .replace("×", "")
                .replace("▽", "")
            )
            for expanded in self._expand_optional_parentheses(text=normalized):
                if expanded:
                    headwords.add(expanded)

        return headwords

    def _expand_optional_parentheses(self, text: str) -> set[str]:
        parts: list[list[str]] = []
        index: int = 0

        while index < len(text):
            if text[index] != "（":
                parts.append([text[index]])
                index += 1
                continue

            end_index: int = text.find("）", index + 1)
            if end_index == -1:
                parts.append([text[index]])
                index += 1
                continue

            optional_text: str = text[index + 1 : end_index]
            parts.append(["", optional_text])
            index: int = end_index + 1

        return {"".join(pattern) for pattern in product(*parts)}


class IWANAMI_DIC(DICTIONARY):
    """
    GSK2010-A-岩波国語辞典第五版2004 (the Corpus of Iwanami Japanese Dictionary Fifth Edition)
    """

    def __init__(self) -> None:
        self.dic_dir_path: Path = Path(
            "dictionaries/GSK2010-A-岩波国語辞典第五版2004/corpus/"
        )
        # All records
        self.records: list[IWANAMI_RECORD] = []
        # Set of headword spellings
        self.headwords: set[str] = set()

        for dic_file in self.dic_dir_path.rglob(pattern="*.dict"):
            record = IWANAMI_RECORD(file_path=dic_file)
            self.records.append(record)
            self.headwords.update(record.headwords)

    def extract_prefix_neg_words(self) -> dict[str, set[str]]:
        """
        Extract prefix-negated words
        """
        # Store results as {prefix: {set of headwords}}
        results: dict[str, set[str]] = {
            prefix: set() for prefix in L.PREFIXES.__args__
        }

        for record in tqdm(self.records):
            for headword in record.headwords:
                # Process each prefix
                for prefix in L.PREFIXES.__args__:
                    # If the word starts with the prefix and the word without the prefix exists as a headword
                    if (
                        headword.startswith(prefix)
                        and len(headword) >= len(prefix) + 2
                        and headword[len(prefix) :] in self.headwords
                    ):
                        results[prefix].add(headword[len(prefix) :])

        return results


class Args(Tap):
    dic: L.DIC


def main(args: Args) -> None:
    if args.dic == "jwd":
        dic = JWD_DIC()
    elif args.dic == "bunruidb":
        dic = BUNRUIDB_DIC()
    elif args.dic == "iwanami":
        dic = IWANAMI_DIC()
    # "all" is not used
    else:
        raise ValueError(f"Unsupported dic: {args.dic}")

    results: dict[str, set[str]] = dic.extract_prefix_neg_words()
    U.save_json(file_path=P.extraction_result_files[args.dic], data=results)


if __name__ == "__main__":
    main(args=Args().parse_args())
