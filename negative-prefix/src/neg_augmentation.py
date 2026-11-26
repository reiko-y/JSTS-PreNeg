import re

import literals as L


class NegationAugmentation:
    """
    negation augmentation for a sentence
    """

    def __init__(
        self, prefix_neg_words: dict[str, list[dict[str, str | bool | None]]]
    ) -> None:
        self.prefix_neg_words: dict[
            str, list[dict[str, str | bool | None]]
        ] = prefix_neg_words
        self.augmented_negs: list[AugmentedNeg] = []

        # num of negation augmentation in a sentence
        self.augmented_num: int | None = None

        # num of correct or revised (by human or LLM) negation augmentation
        # in a sentence
        self.can_be_used_num: int | None = None

    def set_augmented_num(self) -> None:
        self.augmented_num: int = len(self.augmented_negs)

    def set_can_be_used_num(self) -> None:
        self.can_be_used_num: int = sum(
            [
                1
                for aug in self.augmented_negs
                if aug.revision_status == "correct"
                or aug.revision_status == "manual-revision"
                or aug.revision_status == "auto-revision"
            ]
        )

    def add_prefix_neg(self, sentence: str) -> None:
        """
        add prefix negation to the sentence
        """
        augment_id_in_sent: int = 0

        for prefix, word_infos in self.prefix_neg_words.items():
            for word_info in word_infos:
                is_correct: bool | None = word_info.get("is_correct")   # type: ignore  # noqa: E501
                if is_correct is None:
                    raise ValueError("is_correct must not be null")
                if not is_correct:
                    continue

                surface: str | None = word_info["surface"]  # type: ignore
                if surface is None:
                    raise ValueError("surface must not be null")

                for match in re.finditer(
                    pattern=re.escape(pattern=surface), string=sentence
                ):
                    start, end = match.span()

                    # Skip if the prefix is already present
                    if (
                        start >= len(prefix)
                        and sentence[start - len(prefix) : start] == prefix
                    ):
                        continue

                    new_word: str = prefix + surface

                    # Record the replaced part, not the whole sentence
                    aug = AugmentedNeg(
                        id_in_sent=augment_id_in_sent,
                        start=start,
                        end=end,
                        new_text=new_word,
                        revision_status=None,
                        revised_sentence=None,
                    )

                    self.augmented_negs.append(aug)
                    augment_id_in_sent += 1


class AugmentedNeg:
    """
    information of one augmentation
    (not for one sentence)
    """

    def __init__(
        self,
        id_in_sent: int,
        start: int,
        end: int,
        new_text: str,
        revision_status: L.REVISION_STATUS | None,
        revised_sentence: str | None,
    ) -> None:
        # augmentation id in a sentence
        self.id_in_sent: int = id_in_sent

        # position of the augmentation target word
        self.start: int = start
        self.end: int = end

        self.new_text: str = new_text

        self.revision_status: L.REVISION_STATUS | None = revision_status
        self.revised_sentence: str | None = revised_sentence

    def set_revision_status(self, revision_status: L.REVISION_STATUS) -> None:
        if self.revision_status is not None:
            raise ValueError("revision_status is already set.")
        self.revision_status = revision_status

    def set_revised_sentence(self, revised_sentence: str) -> None:
        if self.revised_sentence is not None:
            raise ValueError("revised_sentence is already set.")
        self.revised_sentence = revised_sentence
