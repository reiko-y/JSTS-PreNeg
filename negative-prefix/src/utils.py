import json
from pathlib import Path
from typing import Any


# Convert sets to lists
def convert_set_to_list(obj):
    if isinstance(obj, set):
        return list(sorted(obj))
    raise TypeError(
        f"Object of type {obj.__class__.__name__} is not JSON serializable"
    )


def load_json(file_path: Path | str) -> dict[str, Any] | list[dict[str, Any]]:
    with open(file_path, mode="r", encoding="utf-8") as f:
        data = json.load(fp=f)
    return data


def save_jsonl(file_path: Path | str, data: list[dict[str, Any]]) -> None:
    with open(file_path, mode="w", encoding="utf-8") as f:
        for item in data:
            json_line: str = json.dumps(obj=item, ensure_ascii=False)
            f.write(json_line + "\n")


def save_json(
    file_path: Path | str, data: dict[str, Any] | list[dict[str, Any]]
) -> None:
    with open(file_path, mode="w", encoding="utf-8") as f:
        # Convert elements stored as sets to lists before saving
        # Note: element order is not preserved
        json.dump(
            obj=data,
            fp=f,
            indent=2,
            ensure_ascii=False,
            default=convert_set_to_list,
        )


def load_jsonl(file_path: Path | str) -> list[dict[str, Any]]:

    data = []
    with open(file_path, mode="r", encoding="utf-8") as f:
        for line in f:
            if line == "\n":
                continue

            item = json.loads(s=line)
            data.append(item)

    return data
