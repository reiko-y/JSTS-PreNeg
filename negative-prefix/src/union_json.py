from tap import Tap

import literals as L
import paths as P
import utils as U


class Args(Tap):
    dic: L.DIC


def union_splits(dic: L.DIC) -> dict[str, set[str]]:
    """
    Take and save the union of train, val, and test

    Args:
        dic (L.DIC): dictionary name
    Returns:
        dict[str, set[str]]: union for each prefix
    """
    union: dict[str, set[str]] = {}

    # Take the union over the splits
    for path in P.results_in_jsts_files[dic].values():
        prefix_neg_words: dict[str, list[str]] = U.load_json(path)  # type: ignore  # noqa: E501
        for prefix, words in prefix_neg_words.items():
            if prefix not in union:
                union[prefix] = set()
            union[prefix].update(words)

    return union


def format_union(
    union: dict[str, set[str]],
) -> dict[str, list[dict[str, None | str]]]:
    """
    Convert the union into the format used for manual checking

    Args:
        union (dict[str, set[str]]): union for each prefix

    Returns:
        dict[str, list[dict[str, None | str]]]: formatted data
    """
    formatted: dict[str, list[dict[str, None | str]]] = {
        prefix: [
            {"surface": word, "is_correct": None} for word in sorted(words)
        ]
        for prefix, words in union.items()
    }
    return formatted


def main(args: Args) -> None:
    if args.dic == "all":
        union: dict[str, set[str]] = {}
        for dic in L.DIC.__args__:
            if dic == "all":
                continue
            dic_union: dict[str, set[str]] = union_splits(dic)
            for prefix, words in dic_union.items():
                if prefix not in union:
                    union[prefix] = set()
                union[prefix].update(words)
    elif args.dic in L.DIC.__args__:
        union: dict[str, set[str]] = union_splits(args.dic)
    else:
        raise ValueError(f"Unsupported dic: {args.dic}")

    formatted: dict[str, list[dict[str, None | str]]] = format_union(union)
    # Save as JSON
    U.save_json(file_path=P.union_files[args.dic], data=formatted)


if __name__ == "__main__":
    main(args=Args().parse_args())
