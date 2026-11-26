from typing import Any
from tap import Tap

import literals as L
import paths as P
import utils as U


class Args(Tap):
    split: L.SPLIT


def main(args: Args) -> None:
    prefix_neg_sentences: list[dict[str, Any]] = []
    checked_prefix_neg_pairs: list[dict[str, Any]] = U.load_json(
        file_path=P.checked_prefix_neg_sentences_files[args.split]
    )
    for sentence_pair in checked_prefix_neg_pairs:
        assert len(sentence_pair["sentences"]) == 2
        for sentence in (
            s for s in sentence_pair["sentences"] if s is not None
        ):
            for prefix_neg_sent in sentence["augmented_sentences"]:
                if (
                    prefix_neg_sent["revision_status"] == "correct"
                    or prefix_neg_sent["revision_status"] == "manual-revision"
                    or prefix_neg_sent["revision_status"] == "auto-revision"
                ):
                    prefix_neg_sentences.append(
                        {
                            "sentence_pair_id": sentence_pair[
                                "sentence_pair_id"
                            ],
                            "sent1_or_sent2": sentence["sent1_or_sent2"],
                            "sentence_id": sentence["sentence_id"],
                            "plain_sentence": sentence["plain_sentence"],
                            "id_in_sent": prefix_neg_sent["id_in_sent"],
                            "start": prefix_neg_sent["start"],
                            "end": prefix_neg_sent["end"],
                            "prefix_neg_word": prefix_neg_sent["new_text"],
                            "prefix_neg_sentence": prefix_neg_sent[
                                "revised_sentence"
                            ],
                            "revision_status": prefix_neg_sent[
                                "revision_status"
                            ],
                            "augmented_sentences": []
                        }
                    )

    U.save_json(
        file_path=P.usable_prefix_neg_sentences_files[args.split],
        data=prefix_neg_sentences,
    )


if __name__ == "__main__":
    main(args=Args().parse_args())
