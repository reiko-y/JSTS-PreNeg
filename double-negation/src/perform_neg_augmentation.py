import os
import random

from pathlib import Path
from tap import Tap
from tqdm import tqdm
from typing import get_args, Any

import configs as cfg
import literals as L
import paths as P
import utils as U

from morph_analysis import MorphAnalysis, MorphNodes
from neg_augmentation import NegationAugmentation


class JSTSDataset:
    def __init__(
        self,
        file_path: str,
        split: L.SPLIT,
        dataset_name: str = "jsts",
    ) -> None:

        loaded_json: list[dict[str, Any]] = U.load_jsonl(file_path)

        self.split = split
        self.dataset_name: str = dataset_name
        self.sts_instances: list[STSInstance] = []

        print(f"\nLoading JSTS {self.split} dataset...")
        for sts_instance in tqdm(loaded_json):
            sts_instance = STSInstance(
                sentence_pair_id=sts_instance["sentence_pair_id"],
                yjcaptions_id=sts_instance["yjcaptions_id"],
                sentence1=sts_instance["sentence1"],
                sentence2=sts_instance["sentence2"],
                label=sts_instance["label"],
            )

            self.sts_instances.append(sts_instance)

        print(f"\nLoaded {len(self.sts_instances)} JSTS instances.\n")

    def __len__(self) -> int:
        return len(self.sts_instances)

    def get_item_by_sentence_pair_id(
        self, sentence_pair_id: int
    ) -> "STSInstance":
        for sts_instance in self.sts_instances:
            if sts_instance.sentence_pair_id == sentence_pair_id:
                return sts_instance
        raise ValueError(f"Invalid sentence_pair_id: {sentence_pair_id}")


class JSTSPreNegDataset:

    def __init__(
        self,
        file_path: str,
        split: L.SPLIT,
        dataset_name: str = "jsts-preneg",
    ) -> None:

        # set to True after augmentation
        self.is_augmented: bool = False

        loaded_json: list[dict[str, Any]] = U.load_json(file_path)

        self.split = split
        self.dataset_name: str = dataset_name
        self.sentences: list[PreNegSentence] = []

        print(f"\nLoading JSTS-PreNeg {self.split} dataset...")
        for sentence in tqdm(loaded_json):
            sentence = PreNegSentence(
                sentence_pair_id=sentence["sentence_pair_id"],
                sent1_or_sent2=sentence["sent1_or_sent2"],
                sentence_id=sentence["sentence_id"],
                plain_sentence=sentence["plain_sentence"],
                id_in_sent=sentence["id_in_sent"],
                start=sentence["start"],
                end=sentence["end"],
                prefix_neg_word=sentence["prefix_neg_word"],
                prefix_neg_sentence=sentence["prefix_neg_sentence"],
                revision_status=sentence["revision_status"],
            )

            self.sentences.append(sentence)

        self.aug_stat = AugmentationStatistics()

        print(f"\nLoaded {len(self.sentences)} sentences.\n")

    def __len__(self) -> int:
        return len(self.sentences)

    def _set_is_augmented(self) -> None:
        if self.is_augmented:
            raise ValueError("Augmentation has already been performed.")
        else:
            self.is_augmented = True

    def perform_augmentation(self) -> None:
        """
        create sentences that contain negation cues
        """
        for sentence in self.sentences:
            sentence.perform_augmentation()

            # set augmentation info
            for aug in sentence.neg_augmentation.augmented_negs:
                assert aug.neg_position is not None
                self.aug_stat.update_augmentation_results(
                    s1_or_s2=sentence.sent1_or_sent2,
                    position=aug.neg_position,
                    target_pos=aug.target_pos_simple,
                )

        self._set_is_augmented()

        # save augmented sentences to json file
        if not os.path.exists(
            path=P.auto_double_neg_sentences_files[self.split]
        ):
            U.save_json(
                file_path=P.auto_double_neg_sentences_files[self.split],
                data=[
                    {
                        "sentence_pair_id": sentence.sentence_pair_id,
                        "sent1_or_sent2": sentence.sent1_or_sent2,
                        "sentence_id": sentence.sentence_id,
                        "plain_sentence": sentence.plain_sentence,
                        "id_in_sent": sentence.id_in_sent,
                        "start": sentence.start,
                        "end": sentence.end,
                        "prefix_neg_word": sentence.prefix_neg_word,
                        "prefix_neg_sentence": sentence.prefix_neg_sentence,
                        "revision_status": sentence.revision_status,
                        "augmented_sentences": [
                            {
                                "id_in_sent": aug.id_in_sent,
                                "position": aug.neg_position,
                                "new_text": aug.new_text,
                                "new_sentence": aug.augmented_sent(
                                    sentence.nodes
                                ),
                                "is_correct": aug.is_correct,
                            }
                            for aug in sentence.neg_augmentation.augmented_negs
                        ],
                    }
                    for sentence in self.sentences
                    if sentence.is_augmented
                ],
            )


class DoubleNegPairDataset:

    def __init__(self, split: L.SPLIT, jsts_dataset: JSTSDataset) -> None:
        self.split = split
        self.jsts_dataset = jsts_dataset
        self.neg_instance_ids: set[int] = {
            int(item["sentence_pair_id"])
            for item in U.load_jsonl(
                file_path=P.cue_detection_output_files[self.split]
            )
        }
        self.auto_items: dict[int, list[dict[str, Any]]] = self._load_items(
            file_path=P.auto_double_neg_sentences_files[self.split]
        )

    def _load_items(self, file_path: str) -> dict[int, list[dict[str, Any]]]:
        loaded_items: dict[int, list[dict[str, Any]]] = {}
        for item in U.load_json(file_path):
            sentence_pair_id = int(item["sentence_pair_id"])
            loaded_items.setdefault(sentence_pair_id, []).append(item)
        return loaded_items

    def _selected_augmented_sentences(
        self, source_item: dict[str, Any]
    ) -> list[dict[str, Any] | str]:
        augmented_sentences: list[dict[str, Any] | str] = source_item[
            "augmented_sentences"
        ]

        if len(augmented_sentences) == 0:
            return []

        if isinstance(augmented_sentences[0], dict):
            assert "is_correct" in augmented_sentences[0]
            return [
                aug
                for aug in augmented_sentences
                if isinstance(aug, dict) and aug["is_correct"] is True
            ]
        elif isinstance(augmented_sentences[0], str):
            return [aug for aug in augmented_sentences if isinstance(aug, str)]
        else:
            raise ValueError(
                "Invalid type for augmented_sentences. "
                "Expected dict or str, got "
                f"{type(augmented_sentences[0])}."
            )

    def _source_candidates(
        self, sentence_pair_id: int
    ) -> list[dict[str, Any]]:
        candidates: list[dict[str, Any]] = []

        for source_item in self.auto_items.get(sentence_pair_id, []):
            for augmented_sentence in self._selected_augmented_sentences(
                source_item=source_item
            ):
                candidates.append(
                    {
                        "source_item": source_item,
                        "augmented_sentence": augmented_sentence,
                    }
                )

        return candidates

    def _build_source_aug_info(
        self,
        source_item: dict[str, Any],
        augmented_sentence: dict[str, Any] | str,
    ) -> dict[str, Any]:
        source_aug_info: dict[str, Any] = {
            "plain_sentence": source_item["plain_sentence"],
            "aug_id": source_item["id_in_sent"],
            "start": source_item["start"],
            "end": source_item["end"],
            "prefix_neg_word": source_item["prefix_neg_word"],
            "prefix_neg_sentence": source_item["prefix_neg_sentence"],
            "revision_status": source_item["revision_status"],
        }

        if isinstance(augmented_sentence, dict):
            source_aug_info["selected_augmented_sentence"] = {
                "id_in_sent": augmented_sentence["id_in_sent"],
                "position": augmented_sentence["position"],
                "new_text": augmented_sentence["new_text"],
                "new_sentence": augmented_sentence["new_sentence"],
            }
        else:
            source_aug_info["selected_augmented_sentence"] = {
                "new_sentence": augmented_sentence,
            }

        return source_aug_info

    def _pair_type(
        self,
        left_candidate: dict[str, Any] | None,
        right_candidate: dict[str, Any] | None,
    ) -> L.STS_AUG_COMB_PATTERN:
        if left_candidate is None and right_candidate is None:
            raise ValueError("At least one candidate is required.")
        if right_candidate is None:
            return "s1_neg"
        if left_candidate is None:
            return "s2_neg"
        return "s1_neg_s2_neg"

    def _make_pair_dict(
        self,
        jsts_instance: "STSInstance",
        left_candidate: dict[str, Any] | None,
        right_candidate: dict[str, Any] | None,
    ) -> dict[str, Any]:
        if left_candidate is not None:
            left_source_item = left_candidate["source_item"]
            left_augmented_sentence = left_candidate["augmented_sentence"]
            left_source_aug_info = self._build_source_aug_info(
                source_item=left_source_item,
                augmented_sentence=left_augmented_sentence,
            )

            if isinstance(left_augmented_sentence, dict):
                left_sentence = left_augmented_sentence["new_sentence"]
            else:
                left_sentence = left_augmented_sentence
        else:
            left_source_aug_info = None
            left_sentence = jsts_instance.sentence1_original

        if right_candidate is not None:
            right_source_item = right_candidate["source_item"]
            right_augmented_sentence = right_candidate["augmented_sentence"]
            right_source_aug_info = self._build_source_aug_info(
                source_item=right_source_item,
                augmented_sentence=right_augmented_sentence,
            )

            if isinstance(right_augmented_sentence, dict):
                right_sentence = right_augmented_sentence["new_sentence"]
            else:
                right_sentence = right_augmented_sentence
        else:
            right_source_aug_info = None
            right_sentence = jsts_instance.sentence2_original

        pair_type = self._pair_type(left_candidate, right_candidate)

        if left_candidate is not None and right_candidate is None:
            sentence1 = {
                "sentence": left_sentence,
                "aug": left_source_aug_info,
            }
            sentence2 = {"sentence": right_sentence, "aug": None}
        elif left_candidate is None and right_candidate is not None:
            sentence1 = {"sentence": left_sentence, "aug": None}
            sentence2 = {
                "sentence": right_sentence,
                "aug": right_source_aug_info,
            }
        else:
            sentence1 = {
                "sentence": left_sentence,
                "aug": left_source_aug_info,
            }
            sentence2 = {
                "sentence": right_sentence,
                "aug": right_source_aug_info,
            }

        return {
            "original_sentence_pair_id": jsts_instance.sentence_pair_id,
            "type": pair_type,
            "sentence1": sentence1,
            "sentence2": sentence2,
        }

    def make_new_sts_pairs(
        self,
        output_jsonl_path: str,
        sample_num: int | None = None,
        random_seed: int | None = None,
    ) -> None:
        print("\nMaking new sentence pairs for annotation...")

        output_dicts: list[dict[str, Any]] = []
        counter: int = 0

        random.seed(a=random_seed)

        for jsts_instance in tqdm(self.jsts_dataset.sts_instances):
            sentence_pair_id = jsts_instance.sentence_pair_id
            if sentence_pair_id in self.neg_instance_ids:
                continue

            candidates = self._source_candidates(sentence_pair_id)
            if len(candidates) == 0:
                continue

            left_candidates = [
                candidate
                for candidate in candidates
                if candidate["source_item"]["sent1_or_sent2"] == "s1"
            ]
            right_candidates = [
                candidate
                for candidate in candidates
                if candidate["source_item"]["sent1_or_sent2"] == "s2"
            ]

            pair_dicts: list[dict[str, Any]] = []

            for left_candidate in left_candidates:
                pair_dicts.append(
                    self._make_pair_dict(
                        jsts_instance=jsts_instance,
                        left_candidate=left_candidate,
                        right_candidate=None,
                    )
                )

            for right_candidate in right_candidates:
                pair_dicts.append(
                    self._make_pair_dict(
                        jsts_instance=jsts_instance,
                        left_candidate=None,
                        right_candidate=right_candidate,
                    )
                )

            for left_candidate in left_candidates:
                for right_candidate in right_candidates:
                    pair_dicts.append(
                        self._make_pair_dict(
                            jsts_instance=jsts_instance,
                            left_candidate=left_candidate,
                            right_candidate=right_candidate,
                        )
                    )

            if sample_num is not None:
                pair_dicts = pair_dicts[:sample_num]

            pair_id_in_sentence = 0
            for pair_dict in pair_dicts:
                output_dicts.append(
                    {
                        "id": counter,
                        **pair_dict,
                        "new_pair_id_in_sentence": pair_id_in_sentence,
                    }
                )
                counter += 1
                pair_id_in_sentence += 1

        Path(output_jsonl_path).parent.mkdir(parents=True, exist_ok=True)
        U.save_jsonl(file_path=output_jsonl_path, data=output_dicts)
        print(
            f"\nSaved new sentence pairs for annotation: {output_jsonl_path}"
        )


class STSInstance:
    def __init__(
        self,
        sentence_pair_id: str,
        yjcaptions_id: str,
        sentence1: str,
        sentence2: str,
        label: int,
    ):
        self.sentence_pair_id: int = int(sentence_pair_id)
        self.yjcaptions_id: str = yjcaptions_id

        yj_ids: list[str] = yjcaptions_id.split(sep="-")
        assert len(yj_ids) == 3
        self.image_id: str = yj_ids[0]
        self.sentence1_id: str = yj_ids[1]
        self.sentence2_id: str = yj_ids[2]

        self.sentence1_original = sentence1
        self.sentence2_original = sentence2

        self.sentence1 = Sentence(
            plain_sentence=sentence1,
            sentence_pair_id=self.sentence_pair_id,
            image_id=self.image_id,
            sentence_id=self.sentence1_id,
            sent1_or_sent2="s1",
        )

        self.sentence2 = Sentence(
            plain_sentence=sentence2,
            sentence_pair_id=self.sentence_pair_id,
            image_id=self.image_id,
            sentence_id=self.sentence2_id,
            sent1_or_sent2="s2",
        )

        self.label: int = label

    def perform_augmentation_for_jsts_instance(self) -> None:
        self.sentence1.perform_augmentation()
        self.sentence2.perform_augmentation()


class Sentence:
    """
    sentence for JSTS
    """

    def __init__(
        self,
        plain_sentence: str,
        sentence_pair_id: int,
        image_id: str,
        sentence_id: str,
        sent1_or_sent2: L.STS_S1_OR_S2,
        clean_text: bool = True,
    ) -> None:
        self.plain_sentence = plain_sentence
        self.sentence_pair_id = sentence_pair_id
        self.image_id = image_id
        self.sentence_id = sentence_id
        self.sent1_or_sent2 = sent1_or_sent2

        # pre-processing
        if clean_text:
            self.clean_text()

        # perform morphological analysis and get a root node
        self.nodes: MorphNodes = MorphAnalysis.perform_analysis(self.plain_sentence)

        self.neg_augmentation = NegationAugmentation()

        self.is_augmented: bool | None = None

    def __len__(self) -> int:
        assert len(self.nodes) == self.nodes[-1].position + 1
        return len(self.nodes)

    def is_hand_generated(self) -> bool:
        if "g" in self.sentence_id:
            return True
        else:
            return False

    def clean_text(self) -> None:
        """
        preprocessing for the sentence:
        correct format inconsistency in JSTS data
        """
        self.plain_sentence: str = self.plain_sentence.replace("　", " ")
        self.plain_sentence: str = self.plain_sentence.replace("｡", "。")
        self.plain_sentence: str = self.plain_sentence.replace("。。", "。")

    def set_is_augmented(self, value: bool) -> None:
        assert self.is_augmented is None
        self.is_augmented: bool = value

    def perform_augmentation(self) -> None:
        """
        Perform negation augmentation on the sentence.
        """
        if self.is_augmented is not None:
            raise ValueError("Augmentation has already been performed.")
        else:
            # perform negation augmentation
            self.neg_augmentation.negative_unidic(self.nodes)
            # update augmentation count
            self.neg_augmentation.set_augmented_num()
            # update augmentation info
            if len(self.neg_augmentation.augmented_negs) == 0:
                self.set_is_augmented(value=False)
            else:
                self.set_is_augmented(value=True)

    def display_augmentation_info(self) -> None:
        if self.is_augmented is None:
            raise ValueError("Augmentation has not been performed yet.")
        else:
            print(f"{self.sentence_pair_id=}, {self.sent1_or_sent2}")
            print(f"Original: {self.plain_sentence}")

            if self.is_augmented:
                print("Augmented:")
                for aug in self.neg_augmentation.augmented_negs:
                    print(
                        f"{aug.id_in_sent}: {aug.position} ({aug.neg_position}), {aug.target_pos}, {aug.rule}"
                    )
                    print(f"{aug.augmented_sent(self.nodes)}")
                    print()
                print()
            else:
                print("Not augmented.")
                print()


class PreNegSentence:
    """
    sentence for JSTSPreNeg
    """

    def __init__(
        self,
        sentence_pair_id: int,
        sent1_or_sent2: L.STS_S1_OR_S2,
        sentence_id: str,
        plain_sentence: str,
        id_in_sent: int,
        start: int,
        end: int,
        prefix_neg_word: str,
        prefix_neg_sentence: str,
        revision_status: L.REVISION_STATUS,
        clean_text: bool = True,
    ) -> None:
        self.sentence_pair_id = sentence_pair_id
        self.sent1_or_sent2 = sent1_or_sent2
        self.sentence_id = sentence_id
        self.plain_sentence = plain_sentence
        self.id_in_sent = id_in_sent
        self.start = start
        self.end = end
        self.prefix_neg_word = prefix_neg_word
        self.prefix_neg_sentence = prefix_neg_sentence
        self.revision_status = revision_status

        # pre-processing
        if clean_text:
            self.clean_text()

        # perform morphological analysis and get a root node
        self.nodes = MorphAnalysis.perform_analysis(self.prefix_neg_sentence)

        self.neg_augmentation = NegationAugmentation()

        self.is_augmented: bool | None = None

    def __len__(self) -> int:
        assert len(self.nodes) == self.nodes[-1].position + 1
        return len(self.nodes)

    def is_hand_generated(self) -> bool:
        if "g" in self.sentence_id:
            return True
        else:
            return False

    def clean_text(self) -> None:
        """
        preprocessing for the sentence: correct format inconsistency in JSTS data
        """
        self.plain_sentence: str = self.plain_sentence.replace("　", " ")
        self.plain_sentence: str = self.plain_sentence.replace("｡", "。")
        self.plain_sentence: str = self.plain_sentence.replace("。。", "。")

    def set_is_augmented(self, value: bool) -> None:
        assert self.is_augmented is None
        self.is_augmented: bool = value

    def perform_augmentation(self) -> None:
        """
        Perform negation augmentation on the sentence.
        """
        if self.is_augmented is not None:
            raise ValueError("Augmentation has already been performed.")
        else:
            # perform negation augmentation
            self.neg_augmentation.negative_unidic(self.nodes)
            # update augmentation count
            self.neg_augmentation.set_augmented_num()
            # update augmentation info
            if len(self.neg_augmentation.augmented_negs) == 0:
                self.set_is_augmented(value=False)
            else:
                self.set_is_augmented(value=True)

    def display_augmentation_info(self) -> None:
        if self.is_augmented is None:
            raise ValueError("Augmentation has not been performed yet.")
        else:
            print(f"{self.sentence_pair_id=}, {self.sent1_or_sent2}")
            print(f"Original: {self.plain_sentence}")

            if self.is_augmented:
                print("Augmented:")
                for aug in self.neg_augmentation.augmented_negs:
                    print(
                        f"{aug.id_in_sent}: {aug.position} ({aug.neg_position}), {aug.target_pos}, {aug.rule}"
                    )
                    print(f"{aug.augmented_sent(self.nodes)}")
                    print()
                print()
            else:
                print("Not augmented.")
                print()


class AugmentationStatistics:
    """
    statistics for augmentation and filtering
    """

    def __init__(self) -> None:
        # statistics for augmentation
        self.augmentation_results: dict[
            L.STS_S1_OR_S2,
            dict[L.AUGMENTED_NEG_POSITION, dict[L.AUG_TARGET_POS, int]],
        ] = {
            "s1": {
                "clausal": {"動詞": 0, "形容詞": 0, "形容動詞": 0},
                "sub-clausal": {"動詞": 0, "形容詞": 0, "形容動詞": 0},
            },
            "s2": {
                "clausal": {"動詞": 0, "形容詞": 0, "形容動詞": 0},
                "sub-clausal": {"動詞": 0, "形容詞": 0, "形容動詞": 0},
            },
        }

        # statistics for filtering
        self.filtering_results: dict[
            L.STS_S1_OR_S2,
            dict[
                L.AUGMENTED_NEG_POSITION,
                dict[L.AUG_TARGET_POS, dict[bool, int]],
            ],
        ] = {
            "s1": {
                "clausal": {
                    "動詞": {True: 0, False: 0},
                    "形容詞": {True: 0, False: 0},
                    "形容動詞": {True: 0, False: 0},
                },
                "sub-clausal": {
                    "動詞": {True: 0, False: 0},
                    "形容詞": {True: 0, False: 0},
                    "形容動詞": {True: 0, False: 0},
                },
            },
            "s2": {
                "clausal": {
                    "動詞": {True: 0, False: 0},
                    "形容詞": {True: 0, False: 0},
                    "形容動詞": {True: 0, False: 0},
                },
                "sub-clausal": {
                    "動詞": {True: 0, False: 0},
                    "形容詞": {True: 0, False: 0},
                    "形容動詞": {True: 0, False: 0},
                },
            },
        }

    def display_augmentation_details(self) -> None:
        for key_s1_or_s2 in get_args(L.STS_S1_OR_S2):
            for key_position in get_args(L.AUGMENTED_NEG_POSITION):
                for key_target_pos in get_args(L.AUG_TARGET_POS):
                    print(
                        f"{key_s1_or_s2}, {key_position}, {key_target_pos}: {self.augmentation_results[key_s1_or_s2][key_position][key_target_pos]}"
                    )

    def display_filtering_details(self) -> None:
        for key_s1_or_s2 in get_args(L.STS_S1_OR_S2):
            for key_position in get_args(L.AUGMENTED_NEG_POSITION):
                for key_target_pos in get_args(L.AUG_TARGET_POS):
                    print(
                        f"{key_s1_or_s2}, {key_position}, {key_target_pos}: {self.filtering_results[key_s1_or_s2][key_position][key_target_pos]}"
                    )

    def update_augmentation_results(
        self,
        s1_or_s2: L.STS_S1_OR_S2,
        position: L.AUGMENTED_NEG_POSITION,
        target_pos: L.AUG_TARGET_POS,
        num: int = 1,
    ) -> None:
        if s1_or_s2 not in get_args(L.STS_S1_OR_S2):
            raise ValueError(f"Invalid STS sentence: {s1_or_s2}")
        if position not in get_args(L.AUGMENTED_NEG_POSITION):
            raise ValueError(f"Invalid position: {position}")
        if target_pos not in get_args(L.AUG_TARGET_POS):
            raise ValueError(f"Invalid target position: {target_pos}")

        self.augmentation_results[s1_or_s2][position][target_pos] += num

    def augmented_num_by_s1_or_s2(self, s1_or_s2: L.STS_S1_OR_S2) -> int:
        if s1_or_s2 not in get_args(L.STS_S1_OR_S2):
            raise ValueError(f"Invalid STS sentence: {s1_or_s2}")

        return sum(
            [
                self.augmentation_results[s1_or_s2][position][target_pos]
                for position in get_args(L.AUGMENTED_NEG_POSITION)
                for target_pos in get_args(L.AUG_TARGET_POS)
            ]
        )

    def augmented_num_by_neg_position(
        self, position: L.AUGMENTED_NEG_POSITION
    ) -> int:
        if position not in get_args(L.AUGMENTED_NEG_POSITION):
            raise ValueError(f"Invalid position: {position}")

        return sum(
            [
                self.augmentation_results[s1_or_s2][position][target_pos]
                for s1_or_s2 in get_args(L.STS_S1_OR_S2)
                for target_pos in get_args(L.AUG_TARGET_POS)
            ]
        )

    def augmented_num_by_target_pos(self, target_pos: L.AUG_TARGET_POS) -> int:
        if target_pos not in get_args(L.AUG_TARGET_POS):
            raise ValueError(f"Invalid target position: {target_pos}")

        return sum(
            [
                self.augmentation_results[s1_or_s2][position][target_pos]
                for s1_or_s2 in get_args(L.STS_S1_OR_S2)
                for position in get_args(L.AUGMENTED_NEG_POSITION)
            ]
        )

    def augmented_num_all(self) -> int:
        if not self._augmented_sum_sanity_check():
            raise ValueError("Augmented numbers are not consistent.")

        return self.augmented_num_by_s1_or_s2(
            "s1"
        ) + self.augmented_num_by_s1_or_s2("s2")

    def _augmented_sum_sanity_check(self) -> bool:
        if (
            self.augmented_num_by_s1_or_s2("s1")
            + self.augmented_num_by_s1_or_s2("s2")
            == self.augmented_num_by_neg_position("clausal")
            + self.augmented_num_by_neg_position("sub-clausal")
            == self.augmented_num_by_target_pos("動詞")
            + self.augmented_num_by_target_pos("形容詞")
            + self.augmented_num_by_target_pos("形容動詞")
        ):
            return True
        else:
            return False

    def update_filtering_results(
        self,
        s1_or_s2: L.STS_S1_OR_S2,
        position: L.AUGMENTED_NEG_POSITION,
        target_pos: L.AUG_TARGET_POS,
        is_correct: bool,
        num: int = 1,
    ) -> None:
        if s1_or_s2 not in get_args(L.STS_S1_OR_S2):
            raise ValueError(f"Invalid STS sentence: {s1_or_s2}")
        if position not in get_args(L.AUGMENTED_NEG_POSITION):
            raise ValueError(f"Invalid position: {position}")
        if target_pos not in get_args(L.AUG_TARGET_POS):
            raise ValueError(f"Invalid target position: {target_pos}")

        self.filtering_results[s1_or_s2][position][target_pos][
            is_correct
        ] += num

    def filtered_num(self, correct_or_incorrect: str) -> int:
        correct_num = sum(
            [
                self.filtering_results[s1_or_s2][position][target_pos][True]
                for s1_or_s2 in get_args(L.STS_S1_OR_S2)
                for position in get_args(L.AUGMENTED_NEG_POSITION)
                for target_pos in get_args(L.AUG_TARGET_POS)
            ]
        )
        incorrect_num = sum(
            [
                self.filtering_results[s1_or_s2][position][target_pos][False]
                for s1_or_s2 in get_args(L.STS_S1_OR_S2)
                for position in get_args(L.AUGMENTED_NEG_POSITION)
                for target_pos in get_args(L.AUG_TARGET_POS)
            ]
        )
        # sanity check
        if correct_num + incorrect_num != self.augmented_num_all():
            raise ValueError("Filtered numbers are not consistent.")

        if correct_or_incorrect == "correct":
            return correct_num
        elif correct_or_incorrect == "incorrect":
            return incorrect_num
        else:
            raise ValueError(
                f"Invalid argument: {correct_or_incorrect}. Specify 'correct' or 'incorrect'."  # noqa: E501
            )


class Args(Tap):
    split: L.SPLIT
    start_idx: int | None = None
    end_idx: int | None = None
    request_api: bool = False


def main(args: Args) -> None:
    prefix_neg_file: str = P.usable_prefix_neg_sentences_files[args.split]
    prefix_neg = JSTSPreNegDataset(file_path=prefix_neg_file, split=args.split)

    jsts_file: str = P.jsts_dataset[args.split]
    jsts = JSTSDataset(file_path=jsts_file, split=args.split)

    prefix_neg.perform_augmentation()

    double_neg = DoubleNegPairDataset(split=args.split, jsts_dataset=jsts)

    double_neg.make_new_sts_pairs(
        output_jsonl_path=P.annotation_target_files[args.split],
        sample_num=None,
        random_seed=cfg.annotation_sampling_random_seed,
    )


if __name__ == "__main__":
    main(args=Args().parse_args())
