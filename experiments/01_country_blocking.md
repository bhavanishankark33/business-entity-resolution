# Experiment 01 — Country Blocking

## Objective

Determine whether country can be used as a lossless first-stage
blocking constraint for candidate generation.

## Dataset Statistics

| Source | Total | US | India |
|---|---:|---:|---:|
| Source 1 | 2,206,821 | 1,323,633 (59.98%) | 883,188 (40.02%) |
| Source 2 | 5,034,616 | 3,016,817 (59.92%) | 2,017,799 (40.08%) |
| Source 3 | 5,285,603 | 3,170,056 (59.98%) | 2,115,547 (40.02%) |

## Ground-Truth Test

Total true matched pairs: 7,638,365

Same-country matches: 7,638,365

Different-country matches: 0

Observed blocking recall: 100%.

## Observation

Every ground-truth S1-S2/S3 match in the training data has the
same country on both records.

## Decision

Use country as the first-stage blocking constraint.

For each S1 entity, only S2 and S3 records belonging to the same
country will be considered for subsequent blocking stages.

## Limitation

Country blocking alone still produces millions of possible
candidates for large country groups, so additional name and
address-based blocking strategies are required.