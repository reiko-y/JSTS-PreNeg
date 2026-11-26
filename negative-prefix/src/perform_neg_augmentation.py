from tqdm.contrib import tenumerate
import os
import random

from pathlib import Path
from typing import Any, Literal
from tap import Tap
from tqdm import tqdm

import configs as cfg
import consts as C
import literals as L
import paths as P
import utils as U

from neg_augmentation import NegationAugmentation


class JSTSDataset:
    def __init__(
        self,
        file_path: str,
        split: L.SPLIT,
        prefix_neg_words: dict[str, list[dict[str, str | bool | None]]],
        dataset_name: str = "jsts",
    ) -> None:
        # set to True after augmentation
        self.is_augmented: bool = False

        loaded_json: list[dict[str, Any]] = U.load_jsonl(file_path)

        self.split: Literal["train", "val", "test"] = split
        self.prefix_neg_words: dict[
            str, list[dict[str, str | bool | None]]
        ] = prefix_neg_words
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
                prefix_neg_words=self.prefix_neg_words,
            )

            self.sts_instances.append(sts_instance)

        self.aug_stat = AugmentationStatistics(
            original_sts_pairs=len(self.sts_instances)
        )

        print(f"\nLoaded {len(self.sts_instances)} STS instances.\n")

    def __len__(self) -> int:
        return len(self.sts_instances)

    def get_item_by_sentence_pair_id(
        self, sentence_pair_id: int
    ) -> "STSInstance":
        for sts_instance in self.sts_instances:
            if sts_instance.sentence_pair_id == sentence_pair_id:
                return sts_instance
        raise ValueError(f"Invalid sentence_pair_id: {sentence_pair_id}")

    def _set_is_augmented(self) -> None:
        if self.is_augmented:
            raise ValueError("Augmentation has already been performed.")
        else:
            self.is_augmented = True

    def get_jsts_neg_instance_indices(self, log_file: str | Path) -> list[int]:
        loaded_json: list[dict[str, Any]] = U.load_jsonl(file_path=log_file)
        negation_contained_pairs_idx: list[int] = [
            int(d["sentence_pair_id"]) for d in loaded_json
        ]

        return negation_contained_pairs_idx

    def extract_overlap(
        self, prefix_neg_words_in_dic: dict[str, list[str]]
    ) -> dict[str, Any]:
        """
        Extract the words that can take a negative prefix and appear in JSTS
        """
        overlap: dict[str, set[str]] = {
            prefix: set() for prefix in prefix_neg_words_in_dic.keys()
        }

        for sts_instance in self.sts_instances:
            for prefix, words in prefix_neg_words_in_dic.items():
                for word in words:
                    if (
                        word in sts_instance.sentence1.plain_sentence
                        or word in sts_instance.sentence2.plain_sentence
                    ):
                        overlap[prefix].add(word)

        return overlap

    def perform_augmentation(self) -> None:
        """
        Add negative prefixes to the JSTS dataset
        """
        for sts_instance in self.sts_instances:
            sts_instance.perform_augmentation_for_jsts_instance()

            # set augmentation info
            # s1
            for aug in sts_instance.sentence1.neg_augmentation.augmented_negs:
                self.aug_stat.update_augmentation_results(s1_or_s2="s1")
            # s2
            for aug in sts_instance.sentence2.neg_augmentation.augmented_negs:
                self.aug_stat.update_augmentation_results(s1_or_s2="s2")

        self._set_is_augmented()

        # save augmented sentences to json file
        if not os.path.exists(path=P.augmented_sentences_files[self.split]):
            U.save_json(
                file_path=P.augmented_sentences_files[self.split],
                data=[
                    {
                        "sentence_pair_id": sts_instance.sentence_pair_id,
                        "sentences": [
                            (
                                {
                                    "sent1_or_sent2": "s1",
                                    "plain_sentence": sts_instance.sentence1_original,  # noqa: E501
                                    "sentence_id": sts_instance.sentence1_id,
                                    "augmented_sentences": [
                                        {
                                            "id_in_sent": aug.id_in_sent,
                                            "start": aug.start,
                                            "end": aug.end,
                                            "original_word": sts_instance.sentence1_original[  # noqa: E501
                                                aug.start : aug.end
                                            ],
                                            "new_text": aug.new_text,
                                            "augmented_sentence": sts_instance.sentence1_original[  # noqa: E501
                                                : aug.start
                                            ]
                                            + aug.new_text
                                            + sts_instance.sentence1_original[
                                                aug.end :
                                            ],
                                            "revision_status": aug.revision_status,  # noqa: E501
                                            "revised_sentence": aug.revised_sentence,  # noqa: E501
                                        }
                                        for aug in sts_instance.sentence1.neg_augmentation.augmented_negs  # noqa: E501
                                    ],
                                }
                                if sts_instance.sentence1.is_augmented
                                else None
                            ),
                            (
                                {
                                    "sent1_or_sent2": "s2",
                                    "plain_sentence": sts_instance.sentence2_original,  # noqa: E501
                                    "sentence_id": sts_instance.sentence2_id,
                                    "augmented_sentences": [
                                        {
                                            "id_in_sent": aug.id_in_sent,
                                            "start": aug.start,
                                            "end": aug.end,
                                            "original_word": sts_instance.sentence2_original[  # noqa: E501
                                                aug.start : aug.end
                                            ],
                                            "new_text": aug.new_text,
                                            "augmented_sentence": sts_instance.sentence2_original[  # noqa: E501
                                                : aug.start
                                            ]
                                            + aug.new_text
                                            + sts_instance.sentence2_original[
                                                aug.end :
                                            ],
                                            "revision_status": aug.revision_status,  # noqa: E501
                                            "revised_sentence": aug.revised_sentence,  # noqa: E501
                                        }
                                        for aug in sts_instance.sentence2.neg_augmentation.augmented_negs  # noqa: E501
                                    ],
                                }
                                if sts_instance.sentence2.is_augmented
                                else None
                            ),
                        ],
                    }
                    for sts_instance in self.sts_instances
                    if sts_instance.sentence1.is_augmented
                    or sts_instance.sentence2.is_augmented
                ],
            )

    def make_sts_pairs(
        self,
        neg_output_jsonl_path: str,
        orig_output_jsonl_path: str,
        sample_num: int | None = None,
        random_seed: int | None = None,
    ) -> None:
        """
        create new sentence pairs
            - neg_output_jsonl_path: output file path for new sentence pairs
            - orig_output_jsonl_path:
                output file path for original sentence pairs
            - sample_num: sampling num
            - random_seed: seed for sampling
        """
        # Set the revision status of sentences after adding negative prefixes
        if os.path.exists(
            path=P.checked_prefix_neg_sentences_files[self.split]
        ):
            self._set_revision_stat(
                prefix_neg_sentence_pairs=U.load_json(
                    file_path=P.checked_prefix_neg_sentences_files[self.split]
                )  # type: ignore
            )
        else:
            print(
                f"\nChecked sentences file not found: {P.checked_prefix_neg_sentences_files[self.split]}"  # noqa: E501
            )
            print(
                "Please check the automatically revised sentences and save the results to the checked sentences file before making new sentence pairs."  # noqa: E501
            )
            return

        idx_all: list[int] = [
            sts.sentence_pair_id for sts in self.sts_instances
        ]

        # load indices of JSTS instances that contain negation cues
        idx_neg: list[int] = self.get_jsts_neg_instance_indices(
            log_file=P.cue_detection_output_files[self.split]
        )

        # indices of JSTS instances that meet the requirements:
        ## neg(s1) = 0, neg(s2) = 0, and (|S1'| > 0 or |S2'| > 0)
        idx_not_neg: list[int] = [
            i
            for i in idx_all
            if i not in idx_neg
            and (
                (
                    self.get_item_by_sentence_pair_id(
                        sentence_pair_id=i
                    ).sentence1.neg_augmentation.can_be_used_num
                    is not None
                    and self.get_item_by_sentence_pair_id(
                        sentence_pair_id=i
                    ).sentence1.neg_augmentation.can_be_used_num
                    > 0  # type: ignore
                )
                or (
                    self.get_item_by_sentence_pair_id(
                        sentence_pair_id=i
                    ).sentence2.neg_augmentation.can_be_used_num
                    is not None
                    and self.get_item_by_sentence_pair_id(
                        sentence_pair_id=i
                    ).sentence2.neg_augmentation.can_be_used_num
                    > 0  # type: ignore
                )
            )
        ]

        # shuffle
        idx_not_neg_shuffled: list[int] = [i for i in idx_not_neg]
        random.seed(a=random_seed)
        random.shuffle(x=idx_not_neg_shuffled)

        if sample_num is None:
            self._make_new_sts_pairs(
                indices=idx_not_neg_shuffled,
                output_jsonl_path=neg_output_jsonl_path,
            )
            self._make_original_sts_pairs(
                indices=idx_not_neg_shuffled,
                output_jsonl_path=orig_output_jsonl_path,
            )

        # sampling
        else:
            pair_counter: int = 0
            end_idx: int | None = 0
            for i, sts_idx in enumerate(iterable=idx_not_neg_shuffled):
                sts_instance = self.get_item_by_sentence_pair_id(
                    sentence_pair_id=sts_idx
                )
                assert (
                    sts_instance.sentence1.neg_augmentation.can_be_used_num
                    and sts_instance.sentence2.neg_augmentation.can_be_used_num
                )
                s1 = sts_instance.sentence1.neg_augmentation.can_be_used_num
                s2 = sts_instance.sentence2.neg_augmentation.can_be_used_num

                pair_counter += s1 + s2 + s1 * s2
                if pair_counter > sample_num:
                    end_idx: int = i
                    break

            if end_idx is None:
                raise ValueError("Sample number is too large.")

            idx_not_neg_sampling: list[int] = [
                i for i in idx_not_neg_shuffled[: end_idx + 1]
            ]
            idx_not_neg_sampling.sort()

            self._make_new_sts_pairs(
                indices=idx_not_neg_sampling,
                output_jsonl_path=neg_output_jsonl_path,
            )
            self._make_original_sts_pairs(
                indices=idx_not_neg_sampling,
                output_jsonl_path=orig_output_jsonl_path,
            )

    def _make_new_sts_pairs(
        self, indices: list[int], output_jsonl_path: str
    ) -> None:
        """
        create new (S1, S2) sentence pairs for JSTS instances
        whose indices are given
        """
        print("\nMaking new sentence pairs for annotation...")

        output_dicts: list[dict] = []
        counter: int = 0

        for sts_idx in tqdm(indices):
            sts_instance: STSInstance = self.get_item_by_sentence_pair_id(
                sentence_pair_id=sts_idx
            )
            if (
                sts_instance.sentence1.neg_augmentation.can_be_used_num
                is not None
                and sts_instance.sentence1.neg_augmentation.can_be_used_num > 0
            ):
                new_dict: list[
                    dict[
                        str,
                        int
                        | str
                        | dict[str, str | dict[str, str | int] | None],
                    ]
                ] = sts_instance.make_new_sentence_pairs(start_id=counter)
                output_dicts.extend(new_dict)
                counter += len(new_dict)
            elif (
                sts_instance.sentence2.neg_augmentation.can_be_used_num
                is not None
                and sts_instance.sentence2.neg_augmentation.can_be_used_num > 0
            ):
                new_dict: list[
                    dict[
                        str,
                        int
                        | str
                        | dict[str, str | dict[str, str | int] | None],
                    ]
                ] = sts_instance.make_new_sentence_pairs(start_id=counter)
                output_dicts.extend(new_dict)
                counter += len(new_dict)

        U.save_jsonl(file_path=output_jsonl_path, data=output_dicts)
        print(
            f"\nSaved new sentence pairs for annotation: {output_jsonl_path}"
        )

    def _make_original_sts_pairs(
        self, indices: list[int], output_jsonl_path: str
    ) -> None:
        """
        create original (S1, S2) sentence pairs for JSTS instances
        and save them to jsonl file
        """
        print("\nMaking original sentence pairs for annotation...")

        output_dicts: list[dict] = []

        for orig_id, sts_idx in tenumerate(iterable=indices):
            sts_instance: STSInstance = self.get_item_by_sentence_pair_id(
                sentence_pair_id=sts_idx
            )
            output_dicts.append(
                {
                    "id": orig_id,
                    "original_sentence_pair_id": sts_instance.sentence_pair_id,
                    "sentence1": {
                        "sentence": sts_instance.sentence1.plain_sentence,
                        "aug": None,
                    },
                    "sentence2": {
                        "sentence": sts_instance.sentence2.plain_sentence,
                        "aug": None,
                    },
                }
            )

        U.save_jsonl(file_path=output_jsonl_path, data=output_dicts)
        print(
            f"\nSaved original sentence pairs for annotation: {output_jsonl_path}"  # noqa: E501
        )

    def _set_revision_stat(
        self, prefix_neg_sentence_pairs: list[dict[str, Any]]
    ) -> None:
        """
        Set the revision status of sentences after adding negative prefixes, based on the manual and automatic revision results
        """
        augmented_instances: list[STSInstance] = [
            sts_instance
            for sts_instance in self.sts_instances
            if sts_instance.sentence1.is_augmented
            or sts_instance.sentence2.is_augmented
        ]

        for sts_instance, prefix_neg_pair in zip(
            augmented_instances, prefix_neg_sentence_pairs
        ):
            assert (
                sts_instance.sentence_pair_id
                == prefix_neg_pair["sentence_pair_id"]
            )

            sentence_map: dict[str, Any] = {
                "s1": sts_instance.sentence1,
                "s2": sts_instance.sentence2,
            }

            for sentence_data in prefix_neg_pair["sentences"]:
                if sentence_data is None:
                    continue

                s1_or_s2: L.STS_S1_OR_S2 = sentence_data["sent1_or_sent2"]
                target_sentence = sentence_map[s1_or_s2]

                aug_map: dict[int, Any] = {
                    aug.id_in_sent: aug
                    for aug in target_sentence.neg_augmentation.augmented_negs
                }

                for augmented_sentence in sentence_data["augmented_sentences"]:
                    aug = aug_map[augmented_sentence["id_in_sent"]]

                    revision_status = augmented_sentence["revision_status"]
                    if revision_status is None:
                        raise ValueError("revision_status must not be None")

                    revised_sentence = augmented_sentence["revised_sentence"]
                    if revised_sentence is None:
                        raise ValueError("revised_sentence must not be None")

                    aug.set_revision_status(revision_status)
                    aug.set_revised_sentence(revised_sentence)

                    self.aug_stat.update_revision_statuses(
                        s1_or_s2=s1_or_s2,
                        revision=revision_status,
                    )

                target_sentence.neg_augmentation.set_can_be_used_num()


class STSInstance:
    def __init__(
        self,
        sentence_pair_id: str,
        yjcaptions_id: str,
        sentence1: str,
        sentence2: str,
        label: int,
        prefix_neg_words: dict[str, list[dict[str, str | bool | None]]],
    ) -> None:
        self.sentence_pair_id: int = int(sentence_pair_id)
        self.yjcaptions_id: str = yjcaptions_id

        yj_ids: list[str] = yjcaptions_id.split(sep="-")
        assert len(yj_ids) == 3
        self.image_id: str = yj_ids[0]
        self.sentence1_id: str = yj_ids[1]
        self.sentence2_id: str = yj_ids[2]

        self.sentence1_original: str = sentence1
        self.sentence2_original: str = sentence2

        self.sentence1 = Sentence(
            plain_sentence=sentence1,
            sentence_pair_id=self.sentence_pair_id,
            image_id=self.image_id,
            sentence_id=self.sentence1_id,
            sent1_or_sent2="s1",
            prefix_neg_words=prefix_neg_words,
        )

        self.sentence2 = Sentence(
            plain_sentence=sentence2,
            sentence_pair_id=self.sentence_pair_id,
            image_id=self.image_id,
            sentence_id=self.sentence2_id,
            sent1_or_sent2="s2",
            prefix_neg_words=prefix_neg_words,
        )

        self.label: int = label

    def perform_augmentation_for_jsts_instance(self) -> None:
        """
        Add negative prefixes to each STS instance in the JSTS dataset
        """
        self.sentence1.perform_augmentation()
        self.sentence2.perform_augmentation()

    def make_new_sentence_pairs(
        self,
        start_id: int,
    ) -> list[
        dict[str, int | str | dict[str, str | dict[str, str | int] | None]]
    ]:

        new_pairs: list[
            dict[str, int | str | dict[str, str | dict[str, str | int] | None]]
        ] = []

        if (
            self.sentence1.neg_augmentation.can_be_used_num == 0
            or self.sentence1.neg_augmentation.can_be_used_num is None
        ) and (
            self.sentence2.neg_augmentation.can_be_used_num == 0
            or self.sentence2.neg_augmentation.can_be_used_num is None
        ):
            raise ValueError(
                "At least one of the sentences must have at least one correct negation."  # noqa: E501
            )
        else:
            id_count: int = 0

            # (S1neg, S2)
            for aug1 in self.sentence1.neg_augmentation.augmented_negs:
                if (
                    aug1.revision_status == "correct"
                    or aug1.revision_status == "manual-revision"
                    or aug1.revision_status == "auto-revision"
                ):
                    new_pairs.append(
                        {
                            "id": start_id + id_count,
                            "original_sentence_pair_id": self.sentence_pair_id,
                            "new_pair_id_in_sentence": id_count,
                            "type": C.AugSentenceType.S1_NEG,
                            "sentence1": {
                                "sentence": aug1.revised_sentence,
                                "aug": {
                                    "aug_id": aug1.id_in_sent,
                                    "prefix_neg_word": aug1.new_text,
                                    "revision_status": aug1.revision_status,
                                },
                            },
                            "sentence2": {
                                "sentence": self.sentence2.plain_sentence,
                                "aug": None,
                            },
                        }
                    )
                    id_count += 1

            # (S1, S2neg)
            for aug2 in self.sentence2.neg_augmentation.augmented_negs:
                if (
                    aug2.revision_status == "correct"
                    or aug2.revision_status == "manual-revision"
                    or aug2.revision_status == "auto-revision"
                ):
                    new_pairs.append(
                        {
                            "id": start_id + id_count,
                            "original_sentence_pair_id": self.sentence_pair_id,
                            "new_pair_id_in_sentence": id_count,
                            "type": C.AugSentenceType.S2_NEG,
                            "sentence1": {
                                "sentence": self.sentence1.plain_sentence,
                                "aug": None,
                            },
                            "sentence2": {
                                "sentence": aug2.revised_sentence,
                                "aug": {
                                    "aug_id": aug2.id_in_sent,
                                    "prefix_neg_word": aug2.new_text,
                                    "revision_status": aug2.revision_status,
                                },
                            },
                        }
                    )
                    id_count += 1

            # (S1neg, S2neg)
            for aug1 in self.sentence1.neg_augmentation.augmented_negs:
                if (
                    aug1.revision_status == "correct"
                    or aug1.revision_status == "manual-revision"
                    or aug1.revision_status == "auto-revision"
                ):
                    for aug2 in self.sentence2.neg_augmentation.augmented_negs:
                        if (
                            aug2.revision_status == "correct"
                            or aug2.revision_status == "manual-revision"
                            or aug2.revision_status == "auto-revision"
                        ):
                            new_pairs.append(
                                {
                                    "id": start_id + id_count,
                                    "original_sentence_pair_id": self.sentence_pair_id,  # noqa: E501
                                    "new_pair_id_in_sentence": id_count,
                                    "type": C.AugSentenceType.S1_NEG_S2_NEG,
                                    "sentence1": {
                                        "sentence": aug1.revised_sentence,
                                        "aug": {
                                            "aug_id": aug1.id_in_sent,
                                            "prefix_neg_word": aug1.new_text,
                                            "revision_status": aug1.revision_status,  # noqa: E501
                                        },
                                    },
                                    "sentence2": {
                                        "sentence": aug2.revised_sentence,
                                        "aug": {
                                            "aug_id": aug2.id_in_sent,
                                            "prefix_neg_word": aug2.new_text,
                                            "revision_status": aug2.revision_status,  # noqa: E501
                                        },
                                    },
                                }
                            )
                            id_count += 1

        return new_pairs


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
        prefix_neg_words: dict[str, list[dict[str, str | bool | None]]],
        clean_text: bool = True,
    ) -> None:
        self.plain_sentence: str = plain_sentence
        self.sentence_pair_id: int = sentence_pair_id
        self.image_id: str = image_id
        self.sentence_id: str = sentence_id
        self.sent1_or_sent2: L.STS_S1_OR_S2 = sent1_or_sent2
        self.prefix_neg_words: dict[
            str, list[dict[str, str | bool | None]]
        ] = prefix_neg_words

        # pre-processing
        if clean_text:
            self.clean_text()

        self.neg_augmentation = NegationAugmentation(prefix_neg_words)

        self.is_augmented: bool | None = None

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
        - perform negation augmentation for the sentence
        - update augmentation info
        """
        if self.is_augmented is not None:
            raise ValueError("Augmentation has already been performed.")
        else:
            # perform negation augmentation
            self.neg_augmentation.add_prefix_neg(sentence=self.plain_sentence)
            # update augmentation count
            self.neg_augmentation.set_augmented_num()
            # update augmentation info
            if len(self.neg_augmentation.augmented_negs) == 0:
                self.set_is_augmented(value=False)
            else:
                self.set_is_augmented(value=True)


class AugmentationStatistics:
    """
    statistics for augmentation and revision
    """

    def __init__(self, original_sts_pairs: int) -> None:
        self.original_sts_pairs: int = original_sts_pairs

        # statistics for augmentation
        self.augmentation_results: dict[L.STS_S1_OR_S2, int] = {
            "s1": 0,
            "s2": 0,
        }

        # statistics for revision
        self.revision_statuses: dict[
            L.STS_S1_OR_S2, dict[L.REVISION_STATUS, int]
        ] = {
            "s1": {revision: 0 for revision in L.REVISION_STATUS.__args__},
            "s2": {revision: 0 for revision in L.REVISION_STATUS.__args__},
        }

    def update_augmentation_results(
        self,
        s1_or_s2: L.STS_S1_OR_S2,
        num: int = 1,
    ) -> None:
        if s1_or_s2 not in L.STS_S1_OR_S2.__args__:
            raise ValueError(f"Invalid STS sentence: {s1_or_s2}")

        self.augmentation_results[s1_or_s2] += num

    def display_augmentation_details(self) -> None:
        for key_s1_or_s2 in L.STS_S1_OR_S2.__args__:
            print(f"{key_s1_or_s2}: {self.augmentation_results[key_s1_or_s2]}")

    def augmented_num_by_s1_or_s2(self, s1_or_s2: L.STS_S1_OR_S2) -> int:
        if s1_or_s2 not in L.STS_S1_OR_S2.__args__:
            raise ValueError(f"Invalid STS sentence: {s1_or_s2}")

        return sum([self.augmentation_results[s1_or_s2]])

    def augmented_num_all(self) -> int:
        return self.augmented_num_by_s1_or_s2(
            s1_or_s2="s1"
        ) + self.augmented_num_by_s1_or_s2(s1_or_s2="s2")

    def display_filtering_details(self) -> None:
        for key_s1_or_s2 in L.STS_S1_OR_S2.__args__:
            for key_revision_status in L.REVISION_STATUS.__args__:
                print(
                    f"{key_s1_or_s2}, {key_revision_status}: {self.revision_statuses[key_s1_or_s2][key_revision_status]}"  # noqa: E501
                )

    def augmented_num_per_instance(self, sentence_or_sts_pair: "str") -> float:
        if sentence_or_sts_pair == "sentence":
            return self.augmented_num_all() / (self.original_sts_pairs * 2)
        elif sentence_or_sts_pair == "sts_pair":
            return self.augmented_num_all() / self.original_sts_pairs
        else:
            raise ValueError(
                f"Invalid argument: {sentence_or_sts_pair}. Specify 'sentence' or 'sts_pair'."  # noqa: E501
            )

    def update_revision_statuses(
        self,
        s1_or_s2: L.STS_S1_OR_S2,
        revision: L.REVISION_STATUS,
        num: int = 1,
    ) -> None:
        if s1_or_s2 not in L.STS_S1_OR_S2.__args__:
            raise ValueError(f"Invalid STS sentence: {s1_or_s2}")
        if revision not in L.REVISION_STATUS.__args__:
            raise ValueError(f"Invalid filtering result: {revision}")

        self.revision_statuses[s1_or_s2][revision] += num


class Args(Tap):
    split: L.SPLIT


def main(args: Args) -> None:
    jsts_file: str = P.jsts_dataset[args.split]
    prefix_neg_words: dict[str, Any] | list[dict[str, Any]] = U.load_json(
        file_path=P.checked_prefix_neg_words_file
    )
    jsts = JSTSDataset(
        file_path=jsts_file,
        split=args.split,
        prefix_neg_words=prefix_neg_words,  # type: ignore
    )

    jsts.perform_augmentation()

    # Revision is performed based on the output of augmentation
    # both manually and automatically, so it is not included in this code.

    jsts.make_sts_pairs(
        neg_output_jsonl_path=P.neg_annotation_target_files[args.split],
        orig_output_jsonl_path=P.orig_annotation_target_files[args.split],
        sample_num=None,
        random_seed=cfg.annotation_sampling_random_seed,
    )


if __name__ == "__main__":
    main(args=Args().parse_args())
