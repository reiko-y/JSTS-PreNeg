from typing import Literal

PREFIXES = Literal["非", "不", "無", "未", "反", "異"]

SPLIT = Literal["train", "val", "test"]
STS_S1_OR_S2 = Literal["s1", "s2"]
REVISION_STATUS = Literal[
    "correct",
    "manual-revision",
    "auto-revision",
    "cannot-revise",
    "auto-revision-failed",
]

AUGMENTED_NEG_POSITION = Literal["clausal", "sub-clausal"]
AUG_TARGET_POS = Literal["動詞", "形容詞", "形容動詞"]

ANNOTATOR = Literal["annotator01", "annotator02", "annotator03"]
STS_LABEL = Literal["5", "4", "3", "2", "1", "0"]

JSTS_ORIGINAL = Literal["original"]
STS_AUG_COMB_PATTERN = Literal["s1_neg", "s2_neg", "s1_neg_s2_neg"]

# S1S2-S1negS2: ((S1, S2), (S1neg, S2)) -> element of M_{single}
# S1S2-S1S2neg: ((S1, S2), (S1, S2neg)) -> element of M_{single}
# S1S2neg-S1negS2neg: ((S1, S2neg), (S1neg, S2neg)) -> element of M_{both}
# S1negS2-S1negS2neg: ((S1neg, S2), (S1neg, S2neg)) -> element of M_{both}
MINIMAL_PAIR_TYPE = Literal[
    "S1S2-S1negS2", "S1S2-S1S2neg", "S1S2neg-S1negS2neg", "S1negS2-S1negS2neg"
]
