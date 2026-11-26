# Extract prefix-negated words from dictionaries (prefix-neg-words/extracted_from_dic/*.json)
# python src/dictionaries.py --dic jwd
# python src/dictionaries.py --dic bunruidb
# python src/dictionaries.py --dic iwanami

# Save, for each split, the extracted words that appear in the JSTS dataset (prefix-neg-words/in_jsts/by_split/*.json)
# python src/extract_overlap.py --dic jwd --split train
# python src/extract_overlap.py --dic jwd --split val
# python src/extract_overlap.py --dic jwd --split test
# python src/extract_overlap.py --dic bunruidb --split train
# python src/extract_overlap.py --dic bunruidb --split val
# python src/extract_overlap.py --dic bunruidb --split test
# python src/extract_overlap.py --dic iwanami --split train
# python src/extract_overlap.py --dic iwanami --split val
# python src/extract_overlap.py --dic iwanami --split test

# Take the union of the results across splits (prefix-neg-words/in_jsts/*.json)
# python src/union_json.py --dic jwd
# python src/union_json.py --dic bunruidb
# python src/union_json.py --dic iwanami
# python src/union_json.py --dic all

# Manual check (prefix-neg-words/checked/*.json)

# For each split, generate sentences containing prefix-negated words (prefix-neg-sentences/augmented/*.json)
# python src/perform_neg_augmentation.py --split train
# python src/perform_neg_augmentation.py --split val
# python src/perform_neg_augmentation.py --split test

# Manual revision (prefix-neg-sentences/manual-revision/*.json)

# Automatic revision (prefix-neg-sentences/auto-revision/*.jsonl)
# python src/batch.py --split train
# python src/batch.py --split val
# python src/batch.py --split test

# Merge the manual and automatic revision results (prefix-neg-sentences/checked/*.json)
# python src/merge_revisions.py --split train
# python src/merge_revisions.py --split val
# python src/merge_revisions.py --split test

# Manual verification (prefix-neg-sentences/checked/*.json)

# Generate new sentence pairs from the revised sentences (annotations/annotation-targets/*.jsonl)
python src/perform_neg_augmentation.py --split train
python src/perform_neg_augmentation.py --split val
python src/perform_neg_augmentation.py --split test

# Annotation (annotations/jsts-{orig, preneg}-annotation-results/{train, valid, test}/*.jsonl)

# Create instances from the annotation results (annotations/annotation-results/*.jsonl) (data/jsts-preneg-v1.3/*.jsonl)
python src/create_jsts_preneg.py --split train
python src/create_jsts_preneg.py --split val
python src/create_jsts_preneg.py --split test
python src/concat_jsts_preneg.py
