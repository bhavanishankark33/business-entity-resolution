# Experiment 02 — Exact Normalized Name Blocking

## Objective

Evaluate whether exact equality of normalized business names can be
used as a candidate-generation strategy.

## Method

Business names were normalized using:

- Unicode NFKC normalization
- Lowercasing
- Punctuation removal
- Whitespace normalization

S2 and S3 records were indexed by their normalized business names.

For each S1 entity, S2/S3 records with the same normalized name were
considered candidates.

## Results

| Metric | Result |
|---|---:|
| Total true pairs | 7,638,365 |
| Recovered true pairs | 1,668,793 |
| Candidate recall | 21.8475% |
| Average candidates per S1 | 9.86 |
| Maximum candidates for one S1 | 1,042 |
| Unique normalized names | 7,657,215 |

## Observation

Exact normalized-name matching produces a very small candidate set,
but it recovers only 21.8475% of the true matched pairs.

The low recall is caused by spelling variations, abbreviations,
additional/missing words, multilingual representations, and other
name transformations.

## Decision

Do not use exact normalized-name blocking as the sole blocking
strategy.

Retain it as one possible blocking key within a multi-key candidate
generation system.

## Next Step

Evaluate approximate name blocking strategies that improve recall
while keeping candidate volume manageable.