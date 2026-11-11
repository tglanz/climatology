# 01. Compact the code and documents

[Detailed implementation plan](01-compaction-plan.md)

**Change:** keep the current computational logic and make the project smaller and easier to follow.

- Remove unused code, unused APIs, obsolete commands, and redundant documents. Check notebooks, scripts, and other callers before deleting them.
- Move repeated reading, calculations, prediction, and plotting into the ML library. Make notebooks and CLI commands call those functions.
- Keep notebooks to experiment settings, library calls, and explanation.
- Split modules by what they do. Use consistent terms for simulations, replicas, windows, targets, splits, and training runs.
- Update comments and documents to describe the retained code. Remove stale instructions, abandoned plans, and comments that merely repeat code.
- Keep the book independent of a particular implementation and correct known documentation errors. Retain useful theory and unique historical results without duplicating project instructions.

**Why:** the project contains obsolete paths and several implementations of the same work. That makes it harder to find what runs, understand it, and change it consistently.

This step does not change formulas, algorithms, normalization, data selection, targets, or model behavior. If two implementations differ, record the difference for step 02 rather than silently choosing one.

**Verify:**

1. Compare representative calculations and predictions before and after moving code. Require the same values, shapes, options, and data selection.
2. Run retained commands and previously working notebooks on small inputs. Require no new failures. Record existing failures separately.
3. Check for broken imports, links, and callers of removed APIs.
4. Review the diff for logic changes, remaining duplicate implementations, and misleading comments or documents.
