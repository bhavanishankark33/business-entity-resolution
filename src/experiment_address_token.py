import csv
import re
import unicodedata
from collections import defaultdict, Counter


S1_FILE = "dataset/train/train_source1.tsv"
S2_FILE = "dataset/train/train_source2.tsv"
S3_FILE = "dataset/train/train_source3.tsv"
GROUND_TRUTH = "dataset/train/train_ground_truth.tsv"

MAX_TOKEN_DF = 5000
SAMPLE_SIZE = 100000


def normalize_text(text):
    if not text:
        return ""

    text = unicodedata.normalize("NFKC", text)
    text = text.lower()

    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def get_address_tokens(text):
    text = normalize_text(text)

    if not text:
        return set()

    tokens = set(text.split())

    # Ignore extremely short alphabetic tokens.
    # Keep numbers because house/building numbers are highly informative.
    useful = set()

    for token in tokens:

        if token.isdigit():
            useful.add(token)

        elif len(token) >= 3:
            useful.add(token)

    return useful


# ============================================================
# STEP 1 — Calculate address-token frequencies
# ============================================================

print("STEP 1 — Calculating address-token frequencies...")

token_df = Counter()

for path in [S2_FILE, S3_FILE]:

    print("Reading:", path)

    with open(path, "r", encoding="utf-8") as f:

        reader = csv.DictReader(f, delimiter="\t")

        for row in reader:

            tokens = get_address_tokens(
                row["business_address"]
            )

            for token in tokens:
                token_df[token] += 1


print()
print("Unique address tokens:", len(token_df))

useful_tokens = {
    token
    for token, count in token_df.items()
    if count <= MAX_TOKEN_DF
}

print("Useful address tokens:", len(useful_tokens))

del token_df


# ============================================================
# STEP 2 — Build country + address-token index
# ============================================================

print()
print("STEP 2 — Building address index...")

index = defaultdict(set)

for path in [S2_FILE, S3_FILE]:

    print("Indexing:", path)

    with open(path, "r", encoding="utf-8") as f:

        reader = csv.DictReader(f, delimiter="\t")

        for row in reader:

            entity_id = row["entity_id"]

            country = row["country"].strip().lower()

            tokens = get_address_tokens(
                row["business_address"]
            )

            for token in tokens:

                if token in useful_tokens:

                    index[(country, token)].add(entity_id)


print()
print("Index built.")
print("Index keys:", len(index))


# ============================================================
# STEP 3 — Load S1 data
# ============================================================

print()
print("STEP 3 — Loading S1...")

s1_data = {}

with open(
    S1_FILE,
    "r",
    encoding="utf-8"
) as f:

    reader = csv.DictReader(f, delimiter="\t")

    for row in reader:

        s1_data[row["entity_id"]] = (
            row["country"].strip().lower(),
            get_address_tokens(
                row["business_address"]
            )
        )


print("S1 loaded:", len(s1_data))


# ============================================================
# STEP 4 — Evaluate sample
# ============================================================

print()
print(
    "STEP 4 — Evaluating",
    SAMPLE_SIZE,
    "S1 entities..."
)

total_true_pairs = 0
recovered_pairs = 0

candidate_total = 0
candidate_max = 0

s1_count = 0


with open(
    GROUND_TRUTH,
    "r",
    encoding="utf-8"
) as gt:

    reader = csv.DictReader(gt, delimiter="\t")

    for row in reader:

        if s1_count >= SAMPLE_SIZE:
            break

        s1_id = row["source1_entity_id"]

        country, tokens = s1_data[s1_id]

        candidates = set()

        for token in tokens:

            if token not in useful_tokens:
                continue

            candidates.update(
                index.get(
                    (country, token),
                    ()
                )
            )

        candidate_count = len(candidates)

        candidate_total += candidate_count

        if candidate_count > candidate_max:
            candidate_max = candidate_count

        matches = row["matched_entity_ids"].strip()

        if matches:

            for entity_id in matches.split(","):

                total_true_pairs += 1

                if entity_id in candidates:
                    recovered_pairs += 1

        s1_count += 1

        if s1_count % 10000 == 0:

            print(
                "Processed:",
                s1_count,
                "/",
                SAMPLE_SIZE
            )


# ============================================================
# RESULTS
# ============================================================

print()
print("=" * 60)
print("EXPERIMENT 05 — ADDRESS TOKEN + COUNTRY BLOCKING")
print("=" * 60)

print("Sample S1 entities:", s1_count)

print("Total true pairs:", total_true_pairs)

print("Recovered true pairs:", recovered_pairs)

if total_true_pairs:

    recall = (
        recovered_pairs /
        total_true_pairs *
        100
    )

else:

    recall = 0


print(
    "Candidate recall:",
    f"{recall:.4f}%"
)

if s1_count:

    average_candidates = (
        candidate_total /
        s1_count
    )

else:

    average_candidates = 0


print(
    "Average candidates per S1:",
    average_candidates
)

print(
    "Maximum candidates for one S1:",
    candidate_max
)