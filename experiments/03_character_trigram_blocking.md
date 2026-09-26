# Experiment 03 — Character Trigram Blocking

## Objective

Evaluate character-level n-gram blocking as a way to recover
business-name variations that exact normalized-name blocking misses.

## Method

Business names were normalized using Unicode NFKC normalization,
lowercasing, punctuation removal, and whitespace normalization.

Each name was represented using character trigrams.

An inverted index was constructed from trigrams to entity IDs.

Very common trigrams occurring in more than 5,000 records were
excluded from the index.

## Configuration

- N-gram size: 3
- Maximum trigram document frequency: 5,000

## Results

| Metric | Result |
|---|---:|
| Total true pairs | 7,638,365 |
| Recovered true pairs | 2,491,847 |
| Candidate recall | 32.6228% |
| Average candidates per S1 | 1,575.09 |
| Maximum candidates for one S1 | 40,079 |

## Comparison

Exact normalized-name blocking achieved 21.8475% recall with
9.86 average candidates per S1.

Character trigram blocking increased recall to 32.6228%, but
increased the average candidate set to 1,575.09 records per S1.

## Observation

Character trigrams provide greater tolerance to spelling and
formatting variations, but the resulting candidate sets are too
large for efficient standalone candidate generation.

## Decision

Do not use character trigram blocking as the sole blocking strategy.

Investigate more selective blocking keys and combinations of
blocking strategies.

## Next Step

Evaluate token-based name blocking and its combination with the
lossless country constraint.