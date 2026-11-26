import dotenv
import json
import os
import time

from openai import OpenAI
from tap import Tap
from typing import Any

import configs as cfg
import literals as L
import paths as P
import utils as U

dotenv.load_dotenv()
# API key should be set in the .env file
api_key: str | None = dotenv.get_key(
    dotenv_path=dotenv.find_dotenv(), key_to_get="OPENAI_API_KEY"
)
_client = OpenAI(api_key=api_key)


class Args(Tap):
    split: L.SPLIT


def prepare_batch_input(
    file_path: str, sentence_pairs: list[dict[str, Any]]
) -> None:
    """
    prepare:
    Build the JSONL passed to the Batch API.
    The API is not called at this stage; only the input file is prepared.
    """
    tasks: list[dict[str, Any]] = [
        {
            "custom_id": f"{sentence_pair['sentence_pair_id']}-{sentence['sent1_or_sent2']}-{sentence['sentence_id']}-{augmented_sentence['id_in_sent']}",  # noqa: E501
            "method": "POST",
            "url": "/v1/responses",
            "body": {
                "model": cfg.llm_api_params["model_name"],
                # "temperature": cfg.llm_api_params["temperature"],
                "instructions": cfg.llm_api_params["instructions"],
                "input": f"判定対象：{augmented_sentence['augmented_sentence']}\n残す語：{augmented_sentence['new_text']}",  # noqa: E501
                # "max_output_tokens": cfg.llm_api_params["max_output_tokens"],
                # "seed": cfg.llm_api_params[
                #     "seed"
                # ],
            },
        }
        for sentence_pair in sentence_pairs
        for sentence in (
            s for s in sentence_pair["sentences"] if s is not None
        )
        for augmented_sentence in sentence["augmented_sentences"]
        if augmented_sentence["revision_status"] is None
    ]

    # Save the JSONL file
    U.save_jsonl(file_path, data=tasks)


def request_batch(batch_input: str, batch_output: str) -> None:
    """
    request:
    Upload the JSONL created by prepare to the Files API
    and create a Batch Job with that file as input.
    Wait for the Batch Job to finish, then download and save the results.
    """
    # Load the JSONL file
    jsonl_path: str = batch_input
    with open(file=jsonl_path, mode="rb") as file:
        file_content = file.read()

    # Upload the batch file
    print("Uploading batch file…")
    batch_file = _client.files.create(file=file_content, purpose="batch")
    input_file_id = batch_file.id  # File ID required to create the batch job

    # Create the batch job
    print("Creating batch job…")
    batch_job = _client.batches.create(
        input_file_id=input_file_id,  # ID of the uploaded file
        endpoint="/v1/responses",  # Endpoint to use
        completion_window="24h",  # Fixed at 24h
    )
    job_id = batch_job.id  # ID of the created batch job

    # Poll the batch job status
    print("Polling batch status…")
    while True:
        job = _client.batches.retrieve(batch_id=job_id)
        if job.request_counts is None:
            raise RuntimeError(f"Batch job {job_id} not found.")

        completed = job.request_counts.completed
        total = job.request_counts.total
        status = job.status
        print(f"[{completed}/{total}] status: {status}")
        # Move on once processing is complete
        if status == "completed":
            break
        if status in ("failed", "cancelled"):
            raise RuntimeError(f"Batch job {job_id} failed.")
        # Interval between status checks
        time.sleep(5)

    # Fetch the batch job results
    print("Fetching results…")
    output_id = job.output_file_id
    if output_id is None:
        raise RuntimeError(f"Batch job {job_id} has no output file.")

    result_content = _client.files.content(file_id=output_id).text

    # Pretty-print and save the results
    print("========= Results =========")
    with open(file=batch_output, mode="w", encoding="utf-8") as f:
        for line in result_content.strip().splitlines():
            obj = json.loads(s=line)  # Decode escapes
            f.write(
                json.dumps(obj, ensure_ascii=False) + "\n"
            )  # Write Japanese text as-is
            print(
                json.dumps(obj, ensure_ascii=False, indent=2)
            )  # Pretty-print
    print("===========================")


def main(args: Args) -> None:
    # create a json file for using batch api
    if not os.path.exists(path=P.batch_tasks[args.split]):
        prepare_batch_input(
            file_path=P.batch_tasks[args.split],
            sentence_pairs=U.load_json(
                file_path=P.manually_revised_files[args.split]
            ),  # type: ignore
        )

    # submit batch tasks to the API and save the output
    if not os.path.exists(path=P.batch_results[args.split]):
        request_batch(
            batch_input=P.batch_tasks[args.split],
            batch_output=P.batch_results[args.split],
        )


if __name__ == "__main__":
    main(args=Args().parse_args())
