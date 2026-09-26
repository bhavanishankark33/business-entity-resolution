import csv
import re
import unicodedata
from collections import defaultdict, Counter

S1_FILE = "dataset/train/train_source1.tsv"
S2_FILE = "dataset/train/train_source2.tsv"
S3_FILE = "dataset/train/train_source3.tsv"
GROUND_TRUTH = "dataset/train/train_ground_truth.tsv"

MAX_DF = 5000
SAMPLE_SIZE = 100000


def normalize(text):
    if not text:
        return ""

    text = unicodedata.normalize("NFKC", text)
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def tokens(text):
    text = normalize(text)

    if not text:
        return set()

    return {
        t for t in text.split()
        if len(t) >= 3 or t.isdigit()
    }


# ============================================================
# STEP 1 — Build NAME token frequencies
# ============================================================

print("STEP 1 — Name token frequencies...")

name_df = Counter()

for path in [S2_FILE, S3_FILE]:

    print("Reading:", path)

    with open(path, "r", encoding="utf-8") as f:

        reader = csv.DictReader(f, delimiter="\t")

        for row in reader:

            for token in tokens(row["business_name"]):
                name_df[token] += 1


useful_name = {
    t for t, count in name_df.items()
    if count <= MAX_DF
}

print("Unique name tokens:", len(name_df))
print("Useful name tokens:", len(useful_name))

del name_df


# ============================================================
# STEP 2 — Build ADDRESS token frequencies
# ============================================================

print()
print("STEP 2 — Address token frequencies...")

address_df = Counter()

for path in [S2_FILE, S3_FILE]:

    print("Reading:", path)

    with open(path, "r", encoding="utf-8") as f:

        reader = csv.DictReader(f, delimiter="\t")

        for row in reader:

            for token in tokens(row["business_address"]):
                address_df[token] += 1


useful_address = {
    t for t, count in address_df.items()
    if count <= MAX_DF
}

print("Unique address tokens:", len(address_df))
print("Useful address tokens:", len(useful_address))

del address_df


# ============================================================
# STEP 3 — Build combined country-aware index
# ============================================================

print()
print("STEP 3 — Building combined index...")

name_index = defaultdict(set)
address_index = defaultdict(set)

for path in [S2_FILE, S3_FILE]:

    print("Indexing:", path)

    with open(path, "r", encoding="utf-8") as f:

        reader = csv.DictReader(f, delimiter="\t")

        for row in reader:

            entity_id = row["entity_id"]
            country = row["country"].strip().lower()

            name_tokens = tokens(row["business_name"])
            address_tokens = tokens(row["business_address"])

            for token in name_tokens:

                if token in useful_name:

                    name_index[
                        (country, token)
                    ].add(entity_id)

            for token in address_tokens:

                if token in useful_address:

                    address_index[
                        (country, token)
                    ].add(entity_id)


print("Name index keys:", len(name_index))
print("Address index keys:", len(address_index))


# ============================================================
# STEP 4 — Load S1
# ============================================================

print()
print("STEP 4 — Loading S1...")

s1_data = {}

with open(S1_FILE, "r", encoding="utf-8") as f:

    reader = csv.DictReader(f, delimiter="\t")

    for row in reader:

        s1_data[row["entity_id"]] = (
            row["country"].strip().lower(),
            tokens(row["business_name"]),
            tokens(row["business_address"])
        )


print("S1 loaded:", len(s1_data))


# ============================================================
# STEP 5 — Evaluate
# ============================================================

print()
print(
    "STEP 5 — Evaluating",
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

        country, name_tokens, address_tokens = s1_data[s1_id]

        candidates = set()

        # -----------------------------
        # Name blocking
        # -----------------------------

        for token in name_tokens:

            if token in useful_name:

                candidates.update(
                    name_index.get(
                        (country, token),
                        ()
                    )
                )

        # -----------------------------
        # Address blocking
        # -----------------------------

        for token in address_tokens:

            if token in useful_address:

                candidates.update(
                    address_index.get(
                        (country, token),
                        ()
                    )
                )

        candidate_count = len(candidates)

        candidate_total += candidate_count

        candidate_max = max(
            candidate_max,
            candidate_count
        )

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
print("EXPERIMENT 06 — NAME + ADDRESS + COUNTRY BLOCKING")
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