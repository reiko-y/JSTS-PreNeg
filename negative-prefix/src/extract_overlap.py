from tap import Tap

from perform_neg_augmentation import JSTSDataset

import literals as L
import paths as P
import utils as U


class Args(Tap):
    split: L.SPLIT
    dic: L.DIC


def main(args: Args) -> None:
    jsts_file: str = P.jsts_dataset[args.split]
    # prefix_neg_words is not used here, so pass an empty dict
    jsts = JSTSDataset(
        file_path=jsts_file, split=args.split, prefix_neg_words={}
    )

    # Extract and save the prefix-negated words that appear in JSTS ("all" is not used)
    U.save_json(
        file_path=P.results_in_jsts_files[args.dic][args.split],
        data=jsts.extract_overlap(
            prefix_neg_words_in_dic=U.load_json(file_path=P.extraction_result_files[args.dic])  # type: ignore    # noqa: E501
        ),
    )


if __name__ == "__main__":
    main(args=Args().parse_args())
