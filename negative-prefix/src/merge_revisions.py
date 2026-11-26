from tap import Tap
from typing import Any

import literals as L
import paths as P
import utils as U


class Args(Tap):
    split: L.SPLIT


def merge_revisions(
    manual_revision_path: str, auto_revision_path: str
) -> list[dict[str, Any]]:
    """
    Merge the manual and automatic revision results.
    Load both results and apply the automatic revisions to the manual revision results.
    Return the merged result as JSON.
    """
    # Load the manual and automatic revision results before merging
    manual_revisions: list[dict[str, Any]] = U.load_json(
        file_path=manual_revision_path
    )  # type: ignore
    llm_results: list[dict[str, Any]] = U.load_jsonl(
        file_path=auto_revision_path
    )
    llm_results_iter = iter(llm_results)

    for manual_rev in manual_revisions:
        for sentence in (s for s in manual_rev["sentences"] if s is not None):
            for augmented_sentence in sentence["augmented_sentences"]:
                if augmented_sentence["revision_status"] is None:
                    llm_result: dict[str, Any] = next(llm_results_iter)
                    assert (
                        llm_result["custom_id"]
                        == f"{manual_rev['sentence_pair_id']}-{sentence['sent1_or_sent2']}-{sentence['sentence_id']}-{augmented_sentence['id_in_sent']}"  # noqa: E501
                    )
                    assert (
                        len(llm_result["response"]["body"]["output"]) == 2
                        and llm_result["response"]["body"]["output"][0]["type"]
                        == "reasoning"
                        and llm_result["response"]["body"]["output"][1]["type"]
                        == "message"
                        and len(
                            llm_result["response"]["body"]["output"][1][
                                "content"
                            ]
                        )
                        == 1
                    )
                    output: str = llm_result["response"]["body"]["output"][1][
                        "content"
                    ][0]["text"]

                    if output == "修正不可":
                        augmented_sentence["revision_status"] = "cannot-revise"
                        augmented_sentence["revised_sentence"] = ""
                    else:
                        augmented_sentence["revision_status"] = "auto-revision"
                        augmented_sentence["revised_sentence"] = output

    return manual_revisions


def main(args: Args) -> None:
    # Merge and save
    result: list[dict[str, Any]] = merge_revisions(
        manual_revision_path=P.manually_revised_files[args.split],
        auto_revision_path=P.batch_results[args.split],
    )
    U.save_json(
        file_path=P.checked_prefix_neg_sentences_files[args.split], data=result
    )


if __name__ == "__main__":
    main(args=Args().parse_args())
