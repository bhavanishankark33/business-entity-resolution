import csv


GROUND_TRUTH = "dataset/train/train_ground_truth.tsv"
SOURCE1 = "dataset/train/train_source1.tsv"
SOURCE2 = "dataset/train/train_source2.tsv"
SOURCE3 = "dataset/train/train_source3.tsv"


def load_country(path):
    countries = {}

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")

        for row in reader:
            countries[row["entity_id"]] = row["country"].strip().lower()

    return countries


print("Loading countries...")

s1_country = load_country(SOURCE1)
s2_country = load_country(SOURCE2)
s3_country = load_country(SOURCE3)

print("Loaded.")
print()


same_country = 0
different_country = 0
missing_country = 0

with open(GROUND_TRUTH, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter="\t")

    for row in reader:
        s1_id = row["source1_entity_id"]
        matches = row["matched_entity_ids"].strip()

        if not matches:
            continue

        c1 = s1_country.get(s1_id, "")

        for entity_id in matches.split(","):
            entity_id = entity_id.strip()

            if entity_id.startswith("S2-"):
                c2 = s2_country.get(entity_id, "")
            else:
                c2 = s3_country.get(entity_id, "")

            if not c1 or not c2:
                missing_country += 1
            elif c1 == c2:
                same_country += 1
            else:
                different_country += 1


total = same_country + different_country + missing_country

print("Total true matched pairs:", total)
print("Same country:", same_country)
print("Different country:", different_country)
print("Missing country:", missing_country)

print()

if total:
    print(
        "Same-country percentage:",
        round(same_country / total * 100, 4),
        "%"
    )

    print(
        "Different-country percentage:",
        round(different_country / total * 100, 4),
        "%"
    )