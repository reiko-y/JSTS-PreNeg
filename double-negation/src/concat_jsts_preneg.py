from typing import Any, get_args

import literals as L
import paths as P
import utils as U


def main(output_file_path: str) -> None:
    jsts_preneg_all: list[dict[str, Any]] = []
    # Load the data
    for split in get_args(tp=L.SPLIT):
        jsts_preneg_all.extend(
            U.load_jsonl(file_path=P.jsts_preneg_dataset[split])
        )
    # Reassign IDs to ensure they are unique across the combined dataset
    for new_id, instance in enumerate(jsts_preneg_all):
        instance["id"] = new_id

    # Output in JSONL format
    U.save_jsonl(
        file_path=output_file_path,
        data=jsts_preneg_all,
    )

    print(f"\nJSTS-PreNeg dataset was saved to {output_file_path}")
    print()


if __name__ == "__main__":
    main(output_file_path=P.jsts_preneg_file)
