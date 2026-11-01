# 14. Correct evaluation and research claims

Priority: P1. Contains both document and code logic changes.

## Evidence

`docs/model-evaluation.md:49-56,95` treats replicate spread as a universal lower error bound.
`ml/src/ml/cmd/evaluate.py:305-306` computes a relative-deviation statistic, not the stated standard deviation.
If X reveals Y within one forcing regime, replicate spread can be positive while prediction error is zero.
At line 198, evaluation can replace missing train targets with test targets for its train-mean baseline.
Report assembly can reuse old figures at lines 487,569-570.

The thesis note claims that a scalar profile identifies an invariant measure, that m=0 is inherently more exact than a sampled mean, and that the literature landscape is complete.
`docs/references.md` gives incorrect authors for the practical FNO paper.
The thesis note attributes the invariant-measures paper to the wrong author group.

## Work

Rename the descriptive statistic to replicate variability unless a justified conditional error bound is derived.
Specify estimator, conditioning, averaging unit, sample count, and uncertainty.
Keep train, validation, and test calculations separate. Never substitute test truth for a train baseline.
Write each report from its current artifact manifest so removed sections cannot retain old figures.
State finite-context identifiability and finite-time target uncertainty as assumptions.
Replace absolute novelty and sample-complexity claims with bounded, cited claims.
One target moment does not identify a full invariant measure.
Correct spherical formulas and truncation claims against primary sources and pinned Isca code.
Distinguish registered diagnostic metadata from physical units.

## Verify

1. Add `test_evaluation.py`. An informative-X example with Y=X must permit zero error despite positive replicate spread.
2. An independent-noise example must recover its defined variability statistic. Check exact estimator and denominators.
3. Remove train inputs. Require a clear unavailable-baseline result or error, never a test-derived train mean.
4. Check split-specific grouping on deliberately mixed input manifests.
5. Rerun a report with a section removed. Its prior figures must not appear.
6. Audit every strong claim and citation in the thesis note and existing presentations. Verify titles, authors, assumptions, and quoted passages from the primary source.

Primary checks made during review:
[Practical FNO paper](https://arxiv.org/abs/2512.01421),
[Invariant measures paper](https://arxiv.org/abs/2306.01187),
[Conditioned stochastic emulator](https://arxiv.org/abs/2509.09599),
[Finite-trajectory learning](https://arxiv.org/abs/2607.22399).
These establish related work, not a complete novelty search.
