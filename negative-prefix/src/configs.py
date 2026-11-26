instruction = """次の日本語の文について、指定された語を残したまま文法的・意味的に正しくなるよう修正してください。ただし、修正は指定された語を残すための必要最低限とし、内容語の削除や追加はしないでください。最低限の修正で正しい文にならない場合は「修正不可」と出力してください。修正後の文または「修正不可」のいずれかのみを出力することを遵守してください。"""  # noqa: E501

llm_api_params: dict[str, str | int | float] = {
    "model_name": "gpt-5.5",    # gpt-5.5-2026-04-23
    "instructions": instruction,
    # "max_output_tokens": 32,
    # "temperature": 0.0,
    # "seed": 42,
}

annotation_sampling_random_seed: int = 0
