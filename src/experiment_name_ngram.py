import csv
import re
import unicodedata
from collections import defaultdict, Counter


S1_FILE = "dataset/train/train_source1.tsv"
S2_FILE = "dataset/train/train_source2.tsv"
S3_FILE = "dataset/train/train_source3.tsv"
GROUND_TRUTH = "dataset/train/train_ground_truth.tsv"


N = 3

# Ignore extremely common trigrams.
MAX_DF = 5000


def normalize_name(text):
    if not text:
        return ""

    text = unicodedata.normalize("NFKC", text)
    text = text.lower()

    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def get_ngrams(text):
    """
    Character trigrams.

    Padding helps preserve word boundaries.
    """
    text = f"  {text}  "

    if len(text) <= N:
        return {text}

    return {
        text[i:i + N]
        for i in range(len(text) - N + 1)
    }


# ============================================================
# STEP 1 — Read S2 and S3 names
# ============================================================

print("Reading S2 and S3 names...")

records = {}

for path in [S2_FILE, S3_FILE]:

    with open(path, "r", encoding="utf-8") as f:

        reader = csv.DictReader(f, delimiter="\t")

        for row in reader:

            entity_id = row["entity_id"]
            name = normalize_name(row["business_name"])

            records[entity_id] = name


print("Total S2 + S3 records:", len(records))


# ============================================================
# STEP 2 — Calculate trigram document frequency
# ============================================================

print("Calculating trigram frequencies...")

df = Counter()

for name in records.values():

    if not name:
        continue

    grams = get_ngrams(name)

    for gram in grams:
        df[gram] += 1


print("Unique trigrams:", len(df))

# Keep only useful trigrams.
useful_grams = {
    gram
    for gram, count in df.items()
    if count <= MAX_DF
}

print("Useful trigrams:", len(useful_grams))


# ============================================================
# STEP 3 — Build inverted index
# ============================================================

print("Building trigram inverted index...")

index = defaultdict(set)

for entity_id, name in records.items():

    if not name:
        continue

    grams = get_ngrams(name)

    for gram in grams:

        if gram in useful_grams:
            index[gram].add(entity_id)


print("Index built.")


# ============================================================
# STEP 4 — Load S1 names
# ============================================================

print("Reading S1...")

s1_names = {}

with open(S1_FILE, "r", encoding="utf-8") as f:

    reader = csv.DictReader(f, delimiter="\t")

    for row in reader:

        s1_names[row["entity_id"]] = normalize_name(
            row["business_name"]
        )


# ============================================================
# STEP 5 — Evaluate candidate recall
# ============================================================

print("Evaluating candidate recall...")

total_true_pairs = 0
recovered_pairs = 0

candidate_total = 0
candidate_max = 0

s1_count = 0

# We need ground truth grouped by S1.
with open(GROUND_TRUTH, "r", encoding="utf-8") as f:

    reader = csv.DictReader(f, delimiter="\t")

    for row in reader:

        s1_id = row["source1_entity_id"]

        name = s1_names.get(s1_id, "")

        candidates = set()

        if name:

            for gram in get_ngrams(name):

                if gram in index:
                    candidates.update(index[gram])

        candidate_count = len(candidates)

        candidate_total += candidate_count
        candidate_max = max(candidate_max, candidate_count)

        s1_count += 1

        matches = row["matched_entity_ids"].strip()

        if not matches:
            continue

        for entity_id in matches.split(","):

            entity_id = entity_id.strip()

            total_true_pairs += 1

            if entity_id in candidates:
                recovered_pairs += 1


# ============================================================
# RESULTS
# ============================================================

print()
print("=" * 60)
print("EXPERIMENT 03 — CHARACTER TRIGRAM BLOCKING")
print("=" * 60)

print("Total true pairs:", total_true_pairs)
print("Recovered true pairs:", recovered_pairs)

if total_true_pairs:
    recall = recovered_pairs / total_true_pairs * 100
else:
    recall = 0

print("Candidate recall:", f"{recall:.4f}%")

print()

print("Total S1 entities:", s1_count)

print(
    "Average candidates per S1:",
    candidate_total / s1_count
)

print(
    "Maximum candidates for one S1:",
    candidate_max
)