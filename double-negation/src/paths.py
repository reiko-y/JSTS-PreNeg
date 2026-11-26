import literals as L

# JSTS dataset
jsts_dataset: dict[L.SPLIT, str] = {
    "train": "data/jsts-v1.3/train-v1.3.json",
    "val": "data/jsts-v1.3/valid-v1.3.json",
    "test": "data/jsts-v1.3/test-v1.3.json",
}

# Sentences after manual verification of automatic revisions
checked_prefix_neg_sentences_files: dict[L.SPLIT, str] = {
    "train": "prefix-neg/checked_sentences-train.json",
    "val": "prefix-neg/checked_sentences-val.json",
    "test": "prefix-neg/checked_sentences-test.json",
}

# Usable sentences extracted from the verified sentences containing negative prefixes
usable_prefix_neg_sentences_files: dict[L.SPLIT, str] = {
    "train": "prefix-neg/usable_sentences-train.json",
    "val": "prefix-neg/usable_sentences-val.json",
    "test": "prefix-neg/usable_sentences-test.json",
}

# Sentences with the negation cue "ない" or "ず" automatically added by applying rules to sentences containing negative prefixes
auto_double_neg_sentences_files: dict[L.SPLIT, str] = {
    "train": "double-neg/auto_sentences-train.json",
    "val": "double-neg/auto_sentences-val.json",
    "test": "double-neg/auto_sentences-test.json",
}

# new sentence pairs for manual annotation
annotation_target_files: dict[L.SPLIT, str] = {
    "train": "annotations/annotation-targets/train-sampling.jsonl",
    "val": "annotations/annotation-targets/valid-sampling.jsonl",
    "test": "annotations/annotation-targets/test-sampling.jsonl",
}

# negation cue detection output logs
cue_detection_output_files: dict[L.SPLIT, str] = {
    "train": "annotations/jsts_neg_instance/neg_instances-train.jsonl",
    "val": "annotations/jsts_neg_instance/neg_instances-valid.jsonl",
    "test": "annotations/jsts_neg_instance/neg_instances-test.jsonl",
}

# JSTS-PreNeg annotation results
annotation_results_dir: dict[L.SPLIT, str] = {
    "train": "annotations/jsts-preneg-annotation-results/train/",
    "val": "annotations/jsts-preneg-annotation-results/valid/",
    "test": "annotations/jsts-preneg-annotation-results/test/"
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
