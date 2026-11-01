# 05. Fix NetCDF cache and ownership

Priority: P1.

## Evidence

`ml/src/ml/data/isca_segment.py:21,25` checks `if cache`.
A new empty dictionary never receives its first entry.
A probe opened the same segment twice and left the cache empty.
`validate_segment_dataset` closes the dataset supplied by the caller at line 50.
Plot callers validate and then read that same dataset.

## Work

Check whether a cache was supplied, not whether it is nonempty.
Make ownership explicit: the opener closes owned data, validation leaves borrowed data open.
Use deterministic cleanup on success and failure.
Do not infer guaranteed descriptor exhaustion from this defect.

## Verify

1. Add `test_segment_lifetime.py` with a counting fake reader. Two reads of one path with {} must open once and return the same object.
2. Check uncached reads under the documented ownership rule.
3. Validate a borrowed dataset with a close-call spy. Assert zero close calls and then read it. A successful read alone is insufficient because xarray can reopen a closed backend.
4. Force failures during validation and aggregation. Every owned dataset must close exactly once.
5. Repeat on two tiny real NetCDF segments to check the actual xarray backend.
