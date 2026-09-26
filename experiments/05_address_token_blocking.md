# Experiment 05 — Address Token + Country Blocking

## Objective

Evaluate business-address tokens as a candidate-generation strategy
and determine whether address information can recover matches missed
by name-based blocking.

## Method

Business addresses were normalized using Unicode NFKC normalization,
lowercasing, punctuation removal, and whitespace normalization.

Addresses were split into unique tokens.

Numeric tokens were retained because building and street numbers can
provide strong matching signals.

Alphabetic tokens shorter than three characters were ignored.

An inverted index was created using:

    (country, address_token) -> entity IDs

Address tokens occurring in more than 5,000 records were excluded.

A sample of 100,000 S1 entities was evaluated.

## Results

| Metric | Result |
|---|---:|
| S1 sample | 100,000 |
| True matched pairs | 345,997 |
| Recovered true pairs | 297,218 |
| Candidate recall | 85.9019% |
| Average candidates per S1 | 2,459.12 |
| Maximum candidates for one S1 | 24,544 |

## Comparison

Name-based token + country blocking achieved 55.8407% recall with
920.41 average candidates per S1.

Address-token + country blocking achieved 85.9019% recall but
generated substantially larger candidate sets.

## Observation

Address information is substantially more effective than name
information for recovering true entity matches in the evaluated
sample.

Address variations such as abbreviations, reordered components,
formatting differences, and noisy text still allow many true pairs
to share address tokens.

## Decision

Address-token blocking should be retained as an important blocking
component, but should not be used alone because of its large
candidate volume.

## Next Step

Combine complementary name and address blocking keys and investigate
more selective address signals to improve recall while reducing
candidate volume.