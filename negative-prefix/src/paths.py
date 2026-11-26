import literals as L

# JSTS dataset
jsts_dataset: dict[L.SPLIT, str] = {
    "train": "data/jsts-v1.3/train-v1.3.json",
    "val": "data/jsts-v1.3/valid-v1.3.json",
    "test": "data/jsts-v1.3/test-v1.3.json",
}

# Words extracted from dictionaries
extraction_result_files: dict[str, str] = {
    "jwd": "prefix-neg-words/extracted_from_dic/jwd.json",
    "bunruidb": "prefix-neg-words/extracted_from_dic/bunruidb.json",
    "iwanami": "prefix-neg-words/extracted_from_dic/iwanami.json",
}

# Extracted words that appear in the JSTS dataset
results_in_jsts_files: dict[str, dict[str, str]] = {
    "jwd": {
        "train": "prefix-neg-words/in_jsts/by_split/jwd_train.json",
        "val": "prefix-neg-words/in_jsts/by_split/jwd_val.json",
        "test": "prefix-neg-words/in_jsts/by_split/jwd_test.json",
    },
    "bunruidb": {
        "train": "prefix-neg-words/in_jsts/by_split/bunruidb_train.json",
        "val": "prefix-neg-words/in_jsts/by_split/bunruidb_val.json",
        "test": "prefix-neg-words/in_jsts/by_split/bunruidb_test.json",
    },
    "iwanami": {
        "train": "prefix-neg-words/in_jsts/by_split/iwanami_train.json",
        "val": "prefix-neg-words/in_jsts/by_split/iwanami_val.json",
        "test": "prefix-neg-words/in_jsts/by_split/iwanami_test.json",
    },
}

# Union of the per-split JSON files
union_files: dict[str, str] = {
    "jwd": "prefix-neg-words/in_jsts/jwd_in_jsts.json",
    "bunruidb": "prefix-neg-words/in_jsts/bunruidb_in_jsts.json",
    "iwanami": "prefix-neg-words/in_jsts/iwanami_in_jsts.json",
    "all": "prefix-neg-words/in_jsts/all_in_jsts.json",
}

# Checked prefix-negated words
checked_prefix_neg_words_file: str = (
    "prefix-neg-words/checked/all_in_jsts_checked.json"
)

# Sentences with negative prefixes added
augmented_sentences_files: dict[L.SPLIT, str] = {
    "train": "prefix-neg-sentences/augmented/augmented_sentences-train.json",
    "val": "prefix-neg-sentences/augmented/augmented_sentences-val.json",
    "test": "prefix-neg-sentences/augmented/augmented_sentences-test.json",
}

# Sentences after manual revision
manually_revised_files: dict[L.SPLIT, str] = {
    "train": "prefix-neg-sentences/manual-revision/manually_revised_sentences-train.json",  # noqa: E501
    "val": "prefix-neg-sentences/manual-revision/manually_revised_sentences-val.json",  # noqa: E501
    "test": "prefix-neg-sentences/manual-revision/manually_revised_sentences-test.json",    # noqa: E501
}

# JSONL files passed to the Batch API
batch_tasks: dict[L.SPLIT, str] = {
    "train": "prefix-neg-sentences/auto-revision/batch_tasks-train.jsonl",
    "val": "prefix-neg-sentences/auto-revision/batch_tasks-val.jsonl",
    "test": "prefix-neg-sentences/auto-revision/batch_tasks-test.jsonl",
}

# Result files from the Batch API
batch_results: dict[L.SPLIT, str] = {
    "train": "prefix-neg-sentences/auto-revision/batch_results-train.jsonl",
    "val": "prefix-neg-sentences/auto-revision/batch_results-val.jsonl",
    "test": "prefix-neg-sentences/auto-revision/batch_results-test.jsonl",
}

# Sentences after manual verification of automatic revisions
checked_prefix_neg_sentences_files: dict[L.SPLIT, str] = {
    "train": "prefix-neg-sentences/checked/checked_sentences-train.json",
    "val": "prefix-neg-sentences/checked/checked_sentences-val.json",
    "test": "prefix-neg-sentences/checked/checked_sentences-test.json",
}

# negation cue detection output logs
cue_detection_output_files: dict[L.SPLIT, str] = {
    "train": "annotations/jsts_neg_instance/neg_instances-train.jsonl",
    "val": "annotations/jsts_neg_instance/neg_instances-valid.jsonl",
    "test": "annotations/jsts_neg_instance/neg_instances-test.jsonl",
}

# new sentence pairs with negation for manual annotation
neg_annotation_target_files: dict[L.SPLIT, str] = {
    "train": "annotations/annotation-targets/neg-train-sampling.jsonl",
    "val": "annotations/annotation-targets/neg-valid-sampling.jsonl",
    "test": "annotations/annotation-targets/neg-test-sampling.jsonl",
}

# original sentence pairs for manual annotation
orig_annotation_target_files: dict[L.SPLIT, str] = {
    "train": "annotations/annotation-targets/orig-train-sampling.jsonl",
    "val": "annotations/annotation-targets/orig-valid-sampling.jsonl",
    "test": "annotations/annotation-targets/orig-test-sampling.jsonl",
}

# JSTS-PreNeg annotation results
annotation_results_dir: dict[L.SPLIT, str] = {
    "train": "annotations/jsts-preneg-annotation-results/train/",
    "val": "annotations/jsts-preneg-annotation-results/valid/",
    "test": "annotations/jsts-preneg-annotation-results/test/",
}

# D_{orig} annotation results
d_orig_annotation_results_dir: dict[L.SPLIT, str] = {
    "train": "annotations/jsts-orig-annotation-results/train/",
    "val": "annotations/jsts-orig-annotation-results/valid/",
    "test": "annotations/jsts-orig-annotation-results/test/",
}

# JSTS-PreNeg output path
jsts_preneg_dataset: dict[L.SPLIT, str] = {
    "train": "data/jsts-preneg-v1.3/jsts-preneg-train-v1.3.jsonl",
    "val": "data/jsts-preneg-v1.3/jsts-preneg-valid-v1.3.jsonl",
    "test": "data/jsts-preneg-v1.3/jsts-preneg-test-v1.3.jsonl",
}
jsts_preneg_file: str = "data/jsts-preneg-v1.3/jsts-preneg-all-v1.3.jsonl"
