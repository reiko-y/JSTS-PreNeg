import os
import statistics
import literals as L
import paths as P
import utils
from typing import get_args, Literal, Any
from tap import Tap


class AugmentedSentence:
    """
    negation augmented sentence
    """

    def __init__(
        self,
        s1_or_s2: L.STS_S1_OR_S2,
        sentence: str,
        aug: "NegAugmentation | None",
    ) -> None:
        self.s1_or_s2 = s1_or_s2
        self.sentence: str = sentence
        self.aug = aug


class NegAugmentation:
    """
    augmentation information
    """

    def __init__(self, aug_id: int, neg_prefix: L.PREFIXES) -> None:
        self.aug_id: int = aug_id
        self.neg_prefix: L.PREFIXES = neg_prefix


class AnnotatedLabels:
    def __init__(self, labels: dict[L.ANNOTATOR, L.STS_LABEL]) -> None:
        self.label1: L.STS_LABEL = labels["annotator01"]
        self.label2: L.STS_LABEL = labels["annotator02"]
        self.label3: L.STS_LABEL = labels["annotator03"]
        sts_labels: tuple[L.STS_LABEL] = get_args(tp=L.STS_LABEL)
        assert (
            self.label1 in sts_labels
            and self.label2 in sts_labels
            and self.label3 in sts_labels
        )

    def get_median_label(self) -> L.STS_LABEL:
        """
        Returns the median label.
        """

        label_list: list[int] = [
            int(self.label1),
            int(self.label2),
            int(self.label3),
        ]

        median_label: L.STS_LABEL = str(object=statistics.median(data=label_list))  # type: ignore  # noqa: E501
        assert median_label in get_args(tp=L.STS_LABEL)

        return median_label

    def get_count_by_label(self) -> dict[L.STS_LABEL, int]:
        label_counts: dict[L.STS_LABEL, int] = {
            label: 0 for label in get_args(tp=L.STS_LABEL)
        }
        label_counts[self.label1] += 1
        label_counts[self.label2] += 1
        label_counts[self.label3] += 1

        return label_counts


class NegSTSInstance:
    """
    STS instance that contains negation
    (elements of D_{neg})
    """

    def __init__(
        self,
        # ids assigned to randomly sampled data
        sampled_id: int,
        original_sentence_pair_id: int,
        new_pair_id_in_sentence: int,
        type: L.STS_AUG_COMB_PATTERN,
        sentence1: AugmentedSentence,
        sentence2: AugmentedSentence,
        labels: AnnotatedLabels,
    ) -> None:
        self.sampled_id: int = sampled_id
        self.original_sentence_pair_id: int = original_sentence_pair_id
        self.new_pair_id_in_sentence: int = new_pair_id_in_sentence
        self.type: L.STS_AUG_COMB_PATTERN = type
        self.sentence1: AugmentedSentence = sentence1
        self.sentence2: AugmentedSentence = sentence2
        self.labels: AnnotatedLabels = labels


class AugmentedDataset:
    """
    Dataset consisting of augmented STS instances (D_{neg})
    """

    def __init__(self, split: L.SPLIT, jsonl_dir: str) -> None:
        self.split = split
        self.jsonl_dir = jsonl_dir.rstrip("/")
        self.instances: list[NegSTSInstance] = []

        # load jsonl files
        for file in sorted(os.listdir(path=jsonl_dir)):
            if file.endswith(".jsonl"):
                self.instances.extend(
                    self._load_instances(jsonl_file=f"{jsonl_dir}/{file}")
                )

    def _load_instances(self, jsonl_file: str) -> list[NegSTSInstance]:
        return_list: list[NegSTSInstance] = []
        loaded_jsonl: list[dict[str, Any]] = utils.load_jsonl(
            file_path=jsonl_file
        )
        for json in loaded_jsonl:
            neg_sts_instance = NegSTSInstance(
                sampled_id=json["id"],
                original_sentence_pair_id=json["original_sentence_pair_id"],
                new_pair_id_in_sentence=json["new_pair_id_in_sentence"],
                type=json["type"],
                sentence1=AugmentedSentence(
                    s1_or_s2="s1",
                    sentence=json["sentence1"]["sentence"],
                    aug=(
                        None
                        if json["sentence1"]["aug"] is None
                        else NegAugmentation(
                            aug_id=json["sentence1"]["aug"]["aug_id"],
                            neg_prefix=json["sentence1"]["aug"][
                                "prefix_neg_word"
                            ][0],
                        )
                    ),
                ),
                sentence2=AugmentedSentence(
                    s1_or_s2="s2",
                    sentence=json["sentence2"]["sentence"],
                    aug=(
                        None
                        if json["sentence2"]["aug"] is None
                        else NegAugmentation(
                            aug_id=json["sentence2"]["aug"]["aug_id"],
                            neg_prefix=json["sentence2"]["aug"][
                                "prefix_neg_word"
                            ][0],
                        )
                    ),
                ),
                labels=AnnotatedLabels(labels=json["labels"]),
            )
            return_list.append(neg_sts_instance)

        return return_list


class OrigSTSInstance:
    """
    Original STS instance (elements of D_{orig})
    """

    def __init__(
        self,
        # ids assigned to randomly sampled data
        sampled_id: int,
        original_sentence_pair_id: int,
        sentence1: str,
        sentence2: str,
        new_pair_id_in_sentence: int,
        type: L.JSTS_ORIGINAL,
        labels: AnnotatedLabels,
    ) -> None:
        self.sampled_id: int = sampled_id
        self.original_sentence_pair_id: int = original_sentence_pair_id
        self.new_pair_id_in_sentence: int = new_pair_id_in_sentence
        self.type: L.JSTS_ORIGINAL = type
        self.sentence1: str = sentence1
        self.sentence2: str = sentence2
        self.labels: AnnotatedLabels = labels


class OriginalDataset:
    """
    Dataset consisting of original STS instances (D_{orig})
    """

    def __init__(self, split: L.SPLIT, jsonl_dir: str) -> None:
        self.split = split
        self.jsonl_dir = jsonl_dir.rstrip("/")
        self.instances: list[OrigSTSInstance] = []

        # load jsonl files
        for file in sorted(os.listdir(path=jsonl_dir)):
            if file.endswith(".jsonl"):
                self.instances.extend(
                    self._load_instances(jsonl_file=f"{jsonl_dir}/{file}")
                )

    def _load_instances(self, jsonl_file: str) -> list[OrigSTSInstance]:
        loaded_jsonl: list[dict[str, Any]] = utils.load_jsonl(
            file_path=jsonl_file
        )
        return_list: list[OrigSTSInstance] = [
            OrigSTSInstance(
                sampled_id=json["id"],
                original_sentence_pair_id=json["original_sentence_pair_id"],
                sentence1=json["sentence1"]["sentence"],
                sentence2=json["sentence2"]["sentence"],
                new_pair_id_in_sentence=json["pair_id_in_group"],
                type=json["type"],
                labels=AnnotatedLabels(labels=json["labels"]),
            )
            for json in loaded_jsonl
        ]

        return return_list

    def __getitem__(self, sentence_pair_id: int) -> OrigSTSInstance:
        for instance in self.instances:
            if instance.original_sentence_pair_id == sentence_pair_id:
                return instance
        raise ValueError(
            f"Instance with sentence_pair_id {sentence_pair_id} not found"
        )


class JSTSPreNegDataset:
    """
    JSTS-PreNeg dataset (D_{JSTS-PreNeg})
    """

    def __init__(
        self,
        split: L.SPLIT,
        neg_augmented_jsonl_dir: str,
        original_jsonl_dir: str,
    ) -> None:
        self.split = split
        # augmented negation dataset (D_{neg})
        self.augmented_neg_dataset = AugmentedDataset(
            split, neg_augmented_jsonl_dir
        )
        # original dataset (D_{orig})
        self.original_dataset = OriginalDataset(split, original_jsonl_dir)

        # JSTS-PreNeg instances (elements of D_{JSTS-PreNeg})
        self.instances: list[JSTSPreNegInstance] = self._create_dataset()

        # minimal pairs in JSTS-PreNeg (M)
        self.minimal_pairs: list[JSTSPreNegMinimalPair] = (
            self._create_minimal_pairs()
        )

    def _create_minimal_pairs(self) -> list["JSTSPreNegMinimalPair"]:
        minimal_pairs: list["JSTSPreNegMinimalPair"] = []

        jsts_sentence_pair_ids: set[int] = set(
            [instance.jsts_sentence_pair_id for instance in self.instances]
        )

        for jsts_sentence_pair_id in jsts_sentence_pair_ids:
            # JSTS instance by jsts_sentence_pair_id
            instances_by_jsts: list[JSTSPreNegInstance] = [
                instance
                for instance in self.instances
                if instance.jsts_sentence_pair_id == jsts_sentence_pair_id
            ]

            # create minimal pairs (elements of M_{single})
            original_instance: list[JSTSPreNegInstance] = [
                instance
                for instance in instances_by_jsts
                if instance.type == "original"
            ]
            assert len(original_instance) == 1
            for instance in [
                instance
                for instance in instances_by_jsts
                if instance.type in ["s1_neg", "s2_neg"]
            ]:
                minimal_pair_check = JSTSPreNegMinimalPair.check_minimal_pair(
                    instance1=original_instance[0], instance2=instance
                )
                assert minimal_pair_check != "REVERSE"
                if minimal_pair_check is True:
                    minimal_pairs.append(
                        JSTSPreNegMinimalPair(
                            instance1=original_instance[0],
                            instance2=instance,
                            jsts_sentence_pair_id=jsts_sentence_pair_id,
                        )
                    )

            # create minimal pairs (elements of M_{both})
            s1_neg_s2_neg_instances: list[JSTSPreNegInstance] = [
                instance
                for instance in instances_by_jsts
                if instance.type == "s1_neg_s2_neg"
            ]
            for s1_neg_s2_neg_instance in s1_neg_s2_neg_instances:
                for instance in [
                    instance
                    for instance in instances_by_jsts
                    if instance.type in ["s1_neg", "s2_neg"]
                ]:
                    minimal_pair_check = (
                        JSTSPreNegMinimalPair.check_minimal_pair(
                            instance1=instance,
                            instance2=s1_neg_s2_neg_instance,
                        )
                    )
                    assert minimal_pair_check != "REVERSE"
                    if minimal_pair_check is True:
                        minimal_pairs.append(
                            JSTSPreNegMinimalPair(
                                instance1=instance,
                                instance2=s1_neg_s2_neg_instance,
                                jsts_sentence_pair_id=jsts_sentence_pair_id,
                            )
                        )

        return minimal_pairs

    def create_jsonl(self, output_file_path: str) -> None:
        output_list: list[dict[str, Any]] = [
            {
                "id": instance.id,
                "jsts_sentence_pair_id": instance.jsts_sentence_pair_id,
                "pair_id_in_group": instance.pair_id_in_group,
                "type": instance.type,
                "sentence1": {
                    "sentence": instance.sentence1.sentence,
                    "neg": (
                        None
                        if instance.sentence1.neg is None
                        else {
                            "neg_id_in_jsts_sentence": instance.sentence1.neg.neg_id_in_jsts_sentence,  # noqa: E501
                            "neg_prefix": instance.sentence1.neg.neg_prefix,
                        }
                    ),
                },
                "sentence2": {
                    "sentence": instance.sentence2.sentence,
                    "neg": (
                        None
                        if instance.sentence2.neg is None
                        else {
                            "neg_id_in_jsts_sentence": instance.sentence2.neg.neg_id_in_jsts_sentence,  # noqa: E501
                            "neg_prefix": instance.sentence2.neg.neg_prefix,
                        }
                    ),
                },
                "gold_label": instance.gold_label,
                "annotator_labels": instance.annotator_labels,
            }
            for instance in self.instances
        ]

        utils.save_jsonl(output_file_path, data=output_list)
        print(f"\nJSTS-PreNeg dataset was saved to {output_file_path}")
        print()

    def _create_dataset(self) -> list["JSTSPreNegInstance"]:
        return_list: list["JSTSPreNegInstance"] = []

        previous_jsts_sentence_pair_id: int = -1
        id: int = 0
        pair_id_in_group: int = 0
        for neg_instance in self.augmented_neg_dataset.instances:
            # Original Sentence Pair
            if (
                neg_instance.original_sentence_pair_id
                != previous_jsts_sentence_pair_id
            ):
                pair_id_in_group = 0
                jsts_instance: OrigSTSInstance = self.original_dataset[
                    neg_instance.original_sentence_pair_id
                ]
                sentence1 = NegSentence(
                    sentence=jsts_instance.sentence1, neg=None
                )
                sentence2 = NegSentence(
                    sentence=jsts_instance.sentence2, neg=None
                )
                median_label = jsts_instance.labels.get_median_label()
                new_instance_by_jsts = JSTSPreNegInstance(
                    id=id,
                    jsts_sentence_pair_id=jsts_instance.original_sentence_pair_id,  # noqa: E501
                    pair_id_in_group=pair_id_in_group,
                    type="original",
                    sentence1=sentence1,
                    sentence2=sentence2,
                    gold_label=median_label,
                    annotator_labels=jsts_instance.labels.get_count_by_label(),
                )
                return_list.append(new_instance_by_jsts)
                id += 1
                pair_id_in_group += 1

            # Augmented Sentence Pair
            sentence1 = NegSentence(
                sentence=neg_instance.sentence1.sentence,
                neg=(
                    None
                    if neg_instance.sentence1.aug is None
                    else JSTSNegAugmentedNegation(
                        neg_id_in_jsts_sentence=neg_instance.sentence1.aug.aug_id,  # noqa: E501
                        neg_prefix=neg_instance.sentence1.aug.neg_prefix
                    )
                ),
            )
            sentence2 = NegSentence(
                sentence=neg_instance.sentence2.sentence,
                neg=(
                    None
                    if neg_instance.sentence2.aug is None
                    else JSTSNegAugmentedNegation(
                        neg_id_in_jsts_sentence=neg_instance.sentence2.aug.aug_id,  # noqa: E501
                        neg_prefix=neg_instance.sentence2.aug.neg_prefix
                    )
                ),
            )
            median_label = neg_instance.labels.get_median_label()
            new_instance_neg = JSTSPreNegInstance(
                id=id,
                jsts_sentence_pair_id=neg_instance.original_sentence_pair_id,
                pair_id_in_group=pair_id_in_group,
                type=neg_instance.type,
                sentence1=sentence1,
                sentence2=sentence2,
                gold_label=median_label,
                annotator_labels=neg_instance.labels.get_count_by_label(),
            )
            return_list.append(new_instance_neg)

            id += 1
            pair_id_in_group += 1
            previous_jsts_sentence_pair_id: int = (
                neg_instance.original_sentence_pair_id
            )

        return return_list


class JSTSPreNegInstance:
    """
    JSTS-PreNeg instance (element of D_{JSTS-PreNeg})
    """

    def __init__(
        self,
        id: int,
        jsts_sentence_pair_id: int,
        pair_id_in_group: int,  # group id (grouped by JSTS instance)
        type: (
            L.STS_AUG_COMB_PATTERN | L.JSTS_ORIGINAL
        ),  # "original", "s1_neg", "s2_neg", "s1_neg_s2_neg"
        sentence1: "NegSentence",
        sentence2: "NegSentence",
        gold_label: L.STS_LABEL,
        annotator_labels: dict[L.STS_LABEL, int] | None,
    ) -> None:
        self.id: int = id
        self.jsts_sentence_pair_id: int = jsts_sentence_pair_id
        self.pair_id_in_group: int = pair_id_in_group
        self.type: L.STS_AUG_COMB_PATTERN | L.JSTS_ORIGINAL = type
        self.sentence1: NegSentence = sentence1
        self.sentence2: NegSentence = sentence2
        self.gold_label: L.STS_LABEL = gold_label
        self.annotator_labels: dict[L.STS_LABEL, int] | None = annotator_labels


class NegSentence:
    """
    sentence that contains negation
    """

    def __init__(
        self,
        sentence: str,  # plain_sentence
        neg: "JSTSNegAugmentedNegation | None",  # negation info
    ) -> None:
        self.sentence: str = sentence
        self.neg = neg


class JSTSNegAugmentedNegation:
    """
    negation info in augmented sentence
    """

    def __init__(
        self, neg_id_in_jsts_sentence: int, neg_prefix: L.PREFIXES
    ) -> None:
        self.neg_id_in_jsts_sentence: int = neg_id_in_jsts_sentence
        self.neg_prefix: L.PREFIXES = neg_prefix


class JSTSPreNegMinimalPair:
    """
    minimal pair of STS instance
    """

    def __init__(
        self,
        instance1: JSTSPreNegInstance,
        instance2: JSTSPreNegInstance,
        jsts_sentence_pair_id: int,
    ) -> None:
        self.instance1: JSTSPreNegInstance = instance1
        self.instance2: JSTSPreNegInstance = instance2
        self.jsts_sentence_pair_id: int = jsts_sentence_pair_id

        self.type: L.MINIMAL_PAIR_TYPE

        # important negation or not
        self.is_important_negation: bool = (
            True
            if self.instance1.gold_label != self.instance2.gold_label
            else False
        )

        if (
            self.instance1.jsts_sentence_pair_id
            != self.instance2.jsts_sentence_pair_id
        ):
            raise ValueError(
                f"Instances are not from the same JSTS sentence pair: ({self.instance1.jsts_sentence_pair_id}, {self.instance2.jsts_sentence_pair_id})"  # noqa: E501
            )

        # judge minimal pair type
        if (
            self.instance1.type == "original"
            and self.instance2.type == "s1_neg"
        ):
            self.type = "S1S2-S1negS2"
        elif (
            self.instance1.type == "original"
            and self.instance2.type == "s2_neg"
        ):
            self.type = "S1S2-S1S2neg"
        elif (
            self.instance1.type == "s1_neg"
            and self.instance2.type == "s1_neg_s2_neg"
            and self.instance1.sentence1.neg
            and self.instance2.sentence1.neg
            and self.instance1.sentence1.neg.neg_id_in_jsts_sentence
            == self.instance2.sentence1.neg.neg_id_in_jsts_sentence
        ):
            self.type = "S1negS2-S1negS2neg"
        elif (
            self.instance1.type == "s2_neg"
            and self.instance2.type == "s1_neg_s2_neg"
            and self.instance1.sentence2.neg
            and self.instance2.sentence2.neg
            and self.instance1.sentence2.neg.neg_id_in_jsts_sentence
            == self.instance2.sentence2.neg.neg_id_in_jsts_sentence
        ):
            self.type = "S1S2neg-S1negS2neg"
        else:
            raise ValueError(
                f"The pair is not a minimal pair: ({self.instance1.type}, {self.instance2.type})"  # noqa: E501
            )

    @classmethod
    def check_minimal_pair(
        cls, instance1: JSTSPreNegInstance, instance2: JSTSPreNegInstance
    ) -> bool | Literal["REVERSE"]:
        """
        judge if the instance pair is a minimal pair or not
        - True: the pair is a minimal pair
        - REVERSE: the pair is a minimal pair but the order is reversed
        - False: the pair is not a minimal pair
        """
        if instance1.jsts_sentence_pair_id != instance2.jsts_sentence_pair_id:
            return False
        # S1S2-S1negS2
        elif instance1.type == "original" and instance2.type == "s1_neg":
            return True
        # S1S2-S1S2neg
        elif instance1.type == "original" and instance2.type == "s2_neg":
            return True
        # S1negS2-S1negS2neg
        elif (
            instance1.type == "s1_neg"
            and instance2.type == "s1_neg_s2_neg"
            and instance1.sentence1.neg
            and instance2.sentence1.neg
            and instance1.sentence1.neg.neg_id_in_jsts_sentence
            == instance2.sentence1.neg.neg_id_in_jsts_sentence
        ):
            return True
        # S1S2neg-S1negS2neg
        elif (
            instance1.type == "s2_neg"
            and instance2.type == "s1_neg_s2_neg"
            and instance1.sentence2.neg
            and instance2.sentence2.neg
            and instance1.sentence2.neg.neg_id_in_jsts_sentence
            == instance2.sentence2.neg.neg_id_in_jsts_sentence
        ):
            return True
        # REVERSE
        elif instance2.type == "original" and instance1.type == "s1_neg":
            return "REVERSE"
        elif instance2.type == "original" and instance1.type == "s2_neg":
            return "REVERSE"
        elif (
            instance2.type == "s1_neg"
            and instance1.type == "s1_neg_s2_neg"
            and instance2.sentence1.neg
            and instance1.sentence1.neg
            and instance2.sentence1.neg.neg_id_in_jsts_sentence
            == instance1.sentence1.neg.neg_id_in_jsts_sentence
        ):
            return "REVERSE"
        elif (
            instance2.type == "s2_neg"
            and instance1.type == "s1_neg_s2_neg"
            and instance2.sentence2.neg
            and instance1.sentence2.neg
            and instance2.sentence2.neg.neg_id_in_jsts_sentence
            == instance1.sentence2.neg.neg_id_in_jsts_sentence
        ):
            return "REVERSE"
        else:
            return False


class Args(Tap):
    split: L.SPLIT


if __name__ == "__main__":
    args: Args = Args().parse_args()
    jsts_preneg_dataset = JSTSPreNegDataset(
        split=args.split,
        neg_augmented_jsonl_dir=P.annotation_results_dir[args.split],
        original_jsonl_dir=P.d_orig_annotation_results_dir[args.split],
    )
    jsts_preneg_dataset.create_jsonl(
        output_file_path=P.jsts_preneg_dataset[args.split]
    )
