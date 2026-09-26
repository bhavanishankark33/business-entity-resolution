import csv
import re
import unicodedata
from collections import defaultdict, Counter


S1_FILE = "dataset/train/train_source1.tsv"
S2_FILE = "dataset/train/train_source2.tsv"
S3_FILE = "dataset/train/train_source3.tsv"
GROUND_TRUTH = "dataset/train/train_ground_truth.tsv"


# Ignore extremely common tokens.
MAX_TOKEN_DF = 5000


def normalize_text(text):
    if not text:
        return ""

    text = unicodedata.normalize("NFKC", text)
    text = text.lower()

    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def get_tokens(text):
    text = normalize_text(text)

    if not text:
        return set()

    return set(text.split())


# ============================================================
# STEP 1 — Build S2/S3 token index
# ============================================================

print("Building token index...")

# token -> number of records containing token
token_df = Counter()

# Store records temporarily as:
# entity_id -> (country, tokens)
records = {}


for path in [S2_FILE, S3_FILE]:

    print("Reading:", path)

    with open(path, "r", encoding="utf-8") as f:

        reader = csv.DictReader(f, delimiter="\t")

        for row in reader:

            entity_id = row["entity_id"]

            country = row["country"].strip().lower()

            tokens = get_tokens(row["business_name"])

            records[entity_id] = (country, tokens)

            for token in tokens:
                token_df[token] += 1


print()
print("Total S2 + S3 records:", len(records))
print("Unique tokens:", len(token_df))


# ============================================================
# STEP 2 — Remove extremely common tokens
# ============================================================

useful_tokens = {
    token
    for token, count in token_df.items()
    if count <= MAX_TOKEN_DF
}

print("Useful tokens:", len(useful_tokens))


# ============================================================
# STEP 3 — Build country-aware inverted index
# ============================================================

print("Building country-aware token index...")

# (country, token) -> entity IDs
index = defaultdict(set)

for entity_id, (country, tokens) in records.items():

    for token in tokens:

        if token in useful_tokens:
            index[(country, token)].add(entity_id)


print("Index built.")


# We no longer need the full records dictionary.
del records
del token_df


# ============================================================
# STEP 4 — Load S1
# ============================================================

print("Reading S1...")

s1_records = {}

with open(S1_FILE, "r", encoding="utf-8") as f:

    reader = csv.DictReader(f, delimiter="\t")

    for row in reader:

        s1_records[row["entity_id"]] = (
            row["country"].strip().lower(),
            get_tokens(row["business_name"])
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


with open(GROUND_TRUTH, "r", encoding="utf-8") as f:

    reader = csv.DictReader(f, delimiter="\t")

    for row in reader:

        s1_id = row["source1_entity_id"]

        country, tokens = s1_records[s1_id]

        candidates = set()

        for token in tokens:

            if token not in useful_tokens:
                continue

            candidates.update(
                index.get((country, token), set())
            )

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
print("EXPERIMENT 04 — TOKEN NAME + COUNTRY BLOCKING")
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