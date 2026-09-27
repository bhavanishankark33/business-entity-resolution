import csv
import re
import unicodedata


S1_FILE = "dataset/train/train_source1.tsv"
S2_FILE = "dataset/train/train_source2.tsv"
S3_FILE = "dataset/train/train_source3.tsv"
GROUND_TRUTH = "dataset/train/train_ground_truth.tsv"

SAMPLE_SIZE = 100000
MAX_DF = 5000


def normalize(text):
    if not text:
        return ""

    text = unicodedata.normalize("NFKC", text)
    text = text.lower()

    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def get_tokens(text):
    text = normalize(text)

    if not text:
        return set()

    return {
        t for t in text.split()
        if len(t) >= 3 or t.isdigit()
    }


# ============================================================
# STEP 1 — Load S1
# ============================================================

print("Loading S1...")

s1 = {}

with open(S1_FILE, "r", encoding="utf-8") as f:

    reader = csv.DictReader(f, delimiter="\t")

    for row in reader:

        s1[row["entity_id"]] = {
            "name": row["business_name"],
            "address": row["business_address"],
            "country": row["country"].strip().lower(),
            "name_tokens": get_tokens(row["business_name"]),
            "address_tokens": get_tokens(row["business_address"])
        }

print("S1 loaded:", len(s1))


# ============================================================
# STEP 2 — Load S2 + S3
# ============================================================

print()
print("Loading S2 + S3...")

entities = {}

for path in [S2_FILE, S3_FILE]:

    print("Reading:", path)

    with open(path, "r", encoding="utf-8") as f:

        reader = csv.DictReader(f, delimiter="\t")

        for row in reader:

            entities[row["entity_id"]] = {
                "name": row["business_name"],
                "address": row["business_address"],
                "country": row["country"].strip().lower(),
                "name_tokens": get_tokens(row["business_name"]),
                "address_tokens": get_tokens(row["business_address"])
            }

print("S2 + S3 loaded:", len(entities))


# ============================================================
# STEP 3 — Calculate token frequencies
# ============================================================

print()
print("Calculating token frequencies...")

name_df = {}
address_df = {}

for entity in entities.values():

    for token in entity["name_tokens"]:
        name_df[token] = name_df.get(token, 0) + 1

    for token in entity["address_tokens"]:
        address_df[token] = address_df.get(token, 0) + 1


useful_name = {
    token
    for token, count in name_df.items()
    if count <= MAX_DF
}

useful_address = {
    token
    for token, count in address_df.items()
    if count <= MAX_DF
}

del name_df
del address_df

print("Useful name tokens:", len(useful_name))
print("Useful address tokens:", len(useful_address))


# ============================================================
# STEP 4 — Build blocking indexes
# ============================================================

print()
print("Building indexes...")

name_index = {}
address_index = {}

for entity_id, entity in entities.items():

    country = entity["country"]

    for token in entity["name_tokens"]:

        if token not in useful_name:
            continue

        key = (country, token)

        if key not in name_index:
            name_index[key] = set()

        name_index[key].add(entity_id)

    for token in entity["address_tokens"]:

        if token not in useful_address:
            continue

        key = (country, token)

        if key not in address_index:
            address_index[key] = set()

        address_index[key].add(entity_id)


print("Name index keys:", len(name_index))
print("Address index keys:", len(address_index))


# ============================================================
# STEP 5 — Find missed true pairs
# ============================================================

print()
print("Finding missed true pairs...")

missed_pairs = []

s1_count = 0
total_true_pairs = 0
recovered_pairs = 0


with open(
    GROUND_TRUTH,
    "r",
    encoding="utf-8"
) as f:

    reader = csv.DictReader(f, delimiter="\t")

    for row in reader:

        if s1_count >= SAMPLE_SIZE:
            break

        s1_id = row["source1_entity_id"]

        source = s1[s1_id]

        country = source["country"]

        candidates = set()

        # Name blocking
        for token in source["name_tokens"]:

            if token in useful_name:

                candidates.update(
                    name_index.get(
                        (country, token),
                        ()
                    )
                )

        # Address blocking
        for token in source["address_tokens"]:

            if token in useful_address:

                candidates.update(
                    address_index.get(
                        (country, token),
                        ()
                    )
                )

        matches = row["matched_entity_ids"].strip()

        if matches:

            for matched_id in matches.split(","):

                total_true_pairs += 1

                if matched_id in candidates:

                    recovered_pairs += 1

                else:

                    target = entities.get(matched_id)

                    if target:

                        name_overlap = (
                            len(
                                source["name_tokens"]
                                &
                                target["name_tokens"]
                            )
                        )

                        address_overlap = (
                            len(
                                source["address_tokens"]
                                &
                                target["address_tokens"]
                            )
                        )

                        missed_pairs.append({
                            "s1_id": s1_id,
                            "matched_id": matched_id,
                            "s1_name": source["name"],
                            "matched_name": target["name"],
                            "s1_address": source["address"],
                            "matched_address": target["address"],
                            "country": country,
                            "name_overlap": name_overlap,
                            "address_overlap": address_overlap
                        })

        s1_count += 1

        if s1_count % 10000 == 0:

            print(
                "Processed:",
                s1_count,
                "/",
                SAMPLE_SIZE
            )


# ============================================================
# STEP 6 — Save missed pairs
# ============================================================

output_file = "experiments/missed_pairs_sample.tsv"

with open(
    output_file,
    "w",
    encoding="utf-8",
    newline=""
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=[
            "s1_id",
            "matched_id",
            "country",
            "s1_name",
            "matched_name",
            "s1_address",
            "matched_address",
            "name_overlap",
            "address_overlap"
        ],
        delimiter="\t"
    )

    writer.writeheader()

    writer.writerows(missed_pairs)


# ============================================================
# RESULTS
# ============================================================

print()
print("=" * 60)
print("EXPERIMENT 07 — MISSED PAIR ANALYSIS")
print("=" * 60)

print("S1 sample:", s1_count)

print("Total true pairs:", total_true_pairs)

print("Recovered:", recovered_pairs)

print("Missed:", len(missed_pairs))

if total_true_pairs:

    print(
        "Recall:",
        f"{recovered_pairs / total_true_pairs * 100:.4f}%"
    )

print()
print("Saved:", output_file)


# ============================================================
# OVERLAP SUMMARY
# ============================================================

zero_name = 0
zero_address = 0
zero_both = 0

for pair in missed_pairs:

    if pair["name_overlap"] == 0:
        zero_name += 1

    if pair["address_overlap"] == 0:
        zero_address += 1

    if (
        pair["name_overlap"] == 0
        and
        pair["address_overlap"] == 0
    ):
        zero_both += 1


print()
print("Missed pairs with zero name-token overlap:",
      zero_name)

print("Missed pairs with zero address-token overlap:",
      zero_address)

print("Missed pairs with zero overlap in BOTH:",
      zero_both)