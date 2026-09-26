# Experiment 04 — Token + Country Blocking

## Objective

Evaluate whether business-name token overlap combined with the
country constraint can improve candidate recall while remaining
more selective than character n-gram blocking.

## Method

Business names were normalized and split into unique word tokens.

An inverted index was created using:

    (country, token) -> entity IDs

Very common tokens occurring in more than 5,000 records were excluded.

The candidate set for each S1 entity consisted of S2/S3 entities
from the same country that shared at least one useful name token.

## Evaluation

A sample of 100,000 S1 entities was used for the initial evaluation.

## Results

| Metric | Result |
|---|---:|
| S1 sample | 100,000 |
| True matched pairs | 345,997 |
| Recovered true pairs | 193,207 |
| Candidate recall | 55.8407% |
| Average candidates per S1 | 920.41 |
| Maximum candidates per S1 | 12,016 |

## Comparison

Exact normalized-name blocking achieved 21.8475% recall with
9.86 average candidates per S1.

Character trigram blocking achieved 32.6228% recall with
1,575.09 average candidates per S1.

Token + country blocking improved recall to 55.8407% and reduced
average candidate volume compared with trigram blocking.

## Observation

Token overlap is substantially more tolerant of spelling,
abbreviation, and additional-token variations than exact normalized
name matching.

However, many businesses share common tokens, producing large
candidate sets.

## Decision

Do not use token + country blocking as the sole final blocking
strategy.

Use token-based blocking as one component of a multi-key candidate
generation system.

## Next Step

Investigate more selective blocking keys using business-address
information and combinations of name and address signals.