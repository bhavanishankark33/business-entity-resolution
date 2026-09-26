import csv
import re
import unicodedata
from collections import defaultdict


S2_FILE = "dataset/train/train_source2.tsv"
S3_FILE = "dataset/train/train_source3.tsv"
GROUND_TRUTH = "dataset/train/train_ground_truth.tsv"


def normalize_name(text):
    if not text:
        return ""

    text = unicodedata.normalize("NFKC", text)
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text).strip()

    return text


print("Building normalized-name index...")

name_index = defaultdict(set)

# -----------------------------
# Source 2
# -----------------------------

with open(S2_FILE, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter="\t")

    for row in reader:
        name = normalize_name(row["business_name"])

        if name:
            name_index[name].add(row["entity_id"])


print("Source 2 processed.")


# -----------------------------
# Source 3
# -----------------------------

with open(S3_FILE, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter="\t")

    for row in reader:
        name = normalize_name(row["business_name"])

        if name:
            name_index[name].add(row["entity_id"])


print("Source 3 processed.")
print("Unique normalized names:", len(name_index))


# -----------------------------
# Load S1 names
# -----------------------------

s1_names = {}

with open(
    "dataset/train/train_source1.tsv",
    "r",
    encoding="utf-8"
) as f:
    reader = csv.DictReader(f, delimiter="\t")

    for row in reader:
        s1_names[row["entity_id"]] = normalize_name(
            row["business_name"]
        )


# -----------------------------
# Evaluate recall
# -----------------------------

total_true_pairs = 0
recovered_pairs = 0

candidate_total = 0
candidate_max = 0
s1_count = 0

with open(GROUND_TRUTH, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter="\t")

    for row in reader:

        s1_id = row["source1_entity_id"]
        s1_name = s1_names.get(s1_id, "")

        candidates = name_index.get(s1_name, set())

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


print()
print("=" * 60)
print("EXPERIMENT 02 — EXACT NORMALIZED NAME BLOCKING")
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

print("Maximum candidates for one S1:", candidate_max)