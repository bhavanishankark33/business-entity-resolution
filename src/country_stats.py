import csv
from collections import Counter


FILES = [
    "dataset/train/train_source1.tsv",
    "dataset/train/train_source2.tsv",
    "dataset/train/train_source3.tsv",
]


for path in FILES:
    counter = Counter()
    total = 0

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")

        for row in reader:
            country = row["country"].strip()

            if not country:
                country = "<MISSING>"

            counter[country] += 1
            total += 1

    print()
    print("=" * 60)
    print(path)
    print("Total:", total)
    print("Unique countries:", len(counter))
    print("=" * 60)

    for country, count in counter.most_common(20):
        percentage = count / total * 100

        print(
            f"{country:25s} "
            f"{count:10d} "
            f"{percentage:8.2f}%"
        )   