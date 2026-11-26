# Extract the checked sentences containing negative prefixes (prefix-neg/usable_sentences-*.json)
python src/extract_prefix_neg_sentences.py --split train
python src/extract_prefix_neg_sentences.py --split val
python src/extract_prefix_neg_sentences.py --split test

# Add the negation cue "ない" or "ず" to sentences containing negative prefixes

# Manually check the sentences with the negation cue "ない" or "ず" added to sentences containing negative prefixes (double-neg/auto_sentences-*.json)

# Generate new sentence pairs from the checked double-negation sentences (annotations/annotation-targets/*.jsonl)
python src/perform_neg_augmentation.py --split train
python src/perform_neg_augmentation.py --split val
python src/perform_neg_augmentation.py --split test

# Annotation

# Create instances from the annotation results (annotations/jsts-preneg-annotation-results/*.jsonl) (data/jsts-preneg-v1.3/*.jsonl)
python src/create_jsts_preneg.py --split train
python src/create_jsts_preneg.py --split val
python src/create_jsts_preneg.py --split test
python src/concat_jsts_preneg.py
