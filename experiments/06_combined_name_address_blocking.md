# Experiment 06 — Combined Name + Address + Country Blocking

## Objective

Evaluate whether combining complementary name-token and address-token
blocking strategies improves candidate recall.

## Method

For each S1 entity, candidates were generated from:

1. Same-country entities sharing a useful business-name token.
2. Same-country entities sharing a useful business-address token.

The candidate sets from both strategies were combined using a union.

Tokens occurring more than 5,000 times were excluded.

A sample of 100,000 S1 entities was evaluated.

## Results

| Metric | Result |
|---|---:|
| S1 sample | 100,000 |
| True matched pairs | 345,997 |
| Recovered true pairs | 323,582 |
| Candidate recall | 93.5216% |
| Average candidates per S1 | 3,363.01 |
| Maximum candidates for one S1 | 24,544 |

## Comparison

Token + country blocking achieved 55.8407% recall.

Address token + country blocking achieved 85.9019% recall.

Combining name and address token blocking increased recall to
93.5216%.

## Observation

Name and address provide complementary blocking signals.

The combined strategy recovers true pairs missed by either individual
blocking strategy.

However, the union produces a large candidate set, averaging more
than 3,300 candidates per S1 entity.

## Decision

Retain combined name and address blocking as a high-recall candidate
generation strategy, but investigate additional selective blocking
keys and candidate pruning before applying expensive pairwise matching.

## Next Step

Analyze the true matches missed by the combined blocking strategy to
identify the characteristics of the remaining unmatched pairs.  