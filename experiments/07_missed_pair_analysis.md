# Experiment 07 — Missed Pair Analysis

## Objective

Analyze the true entity pairs missed by the combined
name-token and address-token blocking strategy.

## Evaluation

The analysis used the same 100,000 S1 sample used in
Experiment 06.

The combined blocker achieved 93.5216% candidate recall,
leaving 22,415 true pairs outside the candidate set.

## Results

| Metric | Result |
|---|---:|
| S1 sample | 100,000 |
| Total true pairs | 345,997 |
| Recovered pairs | 323,582 |
| Missed pairs | 22,415 |
| Candidate recall | 93.5216% |

### Characteristics of missed pairs

| Condition | Count |
|---|---:|
| Zero name-token overlap | 7,066 |
| Zero address-token overlap | 5,337 |
| Zero overlap in both | 62 |

The categories are not mutually exclusive.

## Observation

Most missed pairs retain some token-level information in either
the business name or business address.

Only 62 missed pairs had zero token overlap in both fields.

This indicates that the remaining blocking failures are primarily
caused by token-level normalization and representation differences
rather than complete absence of useful information.

## Decision

Retain the combined name and address token blocker as the primary
high-recall blocking strategy.

Investigate character-level and normalized representation signals
to recover additional pairs with spelling variations, abbreviations,
transliteration, and formatting differences.

## Next Step

Develop selective character-based blocking/recovery keys and then
move toward pairwise feature extraction and supervised matching.