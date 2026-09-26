import csv
from collections import Counter

GROUND_TRUTH = "dataset/train/train_ground_truth.tsv"

match_counts = []
s2_count = 0
s3_count = 0
zero_match = 0

with open(GROUND_TRUTH, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter="\t")

    for row in reader:
        ids = row["matched_entity_ids"].strip()

        # No matches for this Source-1 entity
        if not ids:
            zero_match += 1
            match_counts.append(0)
            continue

        matches = ids.split(",")

        match_counts.append(len(matches))

        for entity_id in matches:
            if entity_id.startswith("S2-"):
                s2_count += 1
            elif entity_id.startswith("S3-"):
                s3_count += 1


print("Total Source-1 entities:", len(match_counts))
print("Entities with zero matches:", zero_match)

print()
print("Total S2 matches:", s2_count)
print("Total S3 matches:", s3_count)
print("Total matches:", s2_count + s3_count)

print()
print(
    "Average matches per S1:",
    (s2_count + s3_count) / len(match_counts)
)

print(
    "Maximum matches for one S1:",
    max(match_counts)
)

print()
print("Match-count distribution:")

counter = Counter(match_counts)

for count in sorted(counter):
    print(
        count,
        "matches:",
        counter[count]
    )