# Integrity audit

Four checks that decide whether a result can be trusted. They follow the CoE integrity audit used in ScientistOne/ScientistTwo (score verification, specification compliance, reference verification, method-code alignment). ScientistTwo passes all four on 49/49 papers only because each check has a dedicated step in the pipeline; removing any one of them produced sporadic failures. So: run each check at the moment it is cheapest, and run it as a critic (fresh subagent if available, separate explicit step otherwise), never as the author re-reading their own work.

Save reports under `research/07_audit/`.

---

## 1. Score verification - `reproducibility.md`

When: after every full-set run that will be reported, and once more on the final code.

Procedure
1. Start from a clean shell. Run the exact "how to reproduce" command from the report.
2. Compare every reported "ours" number with the regenerated one. Exact match is expected for deterministic code; otherwise state the tolerance and the seed handling.
3. If the script relies on cached artifacts (features, checkpoints), re-derive at least one from scratch and compare (max abs diff).
4. Confirm the script implements the method the report describes (the method may have been refined after the cache was written).

Report

```
# Reproducibility audit
Verdict: Reproducible | Not reproducible
Audited: <path>  (command: ...)

## What I checked
1. Method matches report - <yes/no, one line of evidence>
2. Re-ran the experiment - regenerated numbers:
   - Average <metric>: <value> (reported <value>)
   - Per-dataset: ...
3. Integrity of cached artifacts - <what was re-derived, max abs diff>

Discrepancies: none | <list>
```

---

## 2. Specification compliance - `spec-violation.md`

When: immediately after each experiment, while the diff is small. A failed check discards the result on the spot.

Checklist (each item gets a line with a file:line reference or "none found")
1. Test / OOD / validation leakage - no fitted statistic, threshold, calibration constant, or hyperparameter is computed from data the evaluation uses. Trace every quantity that is *fit* back to the training split.
2. Hardcoded answers - no dataset-specific constants, lookup tables of known results, or branches keyed on dataset name that change the prediction.
3. Evaluator untouched - metric code hash matches `00_setup.md`; no changes to how predictions are scored, thresholded, aggregated, or which samples count.
4. Fair baseline - the baseline numbers in the comparison table come from the same features, splits, seeds, and caps as "ours"; the baseline was not degraded.
5. Determinism and search budget - seeds fixed; no per-dataset hyperparameter search unless the baseline received the same budget; selection rules (if any) use only training-side data.
6. Task rules - any rule the task states (no retraining, parameter budget, latency cap, frozen backbone) is respected.

Report

```
# Specification audit
Audited: <path>   Date:
| Check | Result | Evidence |
|---|---|---|
| Test/OOD leakage | none found | file.py:335-359 fits on ID-train only |
| Hardcoded answers | none found | |
| Evaluator untouched | hash match | |
| Fair baseline | yes | file.py:293-324 same cached features |
| Determinism / search | ok | seeds file.py:94-103; no per-dataset tuning |
| Task rules | ok | |
spec_violation = false | true
```

---

## 3. Reference verification - `references.md`

When: while drafting, for every citation added.

Procedure
- For each citation, record how it was located (search query, DOI/arXiv id, venue page) and the title/authors/year actually found.
- A citation that cannot be located is removed or replaced; a citation whose content does not support the sentence it is attached to is moved or the sentence is changed.
- Do not cite from memory alone; the point of this check is that memory produces plausible, wrong references.

Report: a table `| Citation key | Title found | Where verified | Supports the claim? |` and a count `hallucinated = 0/N`.

---

## 4. Method-code alignment - `method-code.md`

When: on the final code and final draft, after all refinements. This is the audit most often failed by AI-written papers because the method keeps changing after the draft was written.

Procedure
- Walk the method section paragraph by paragraph. For each stated component, equation, default hyperparameter and calibration rule, find the code that implements it and cite file:line.
- Mark each ALIGNED, or describe the discrepancy. A hyperparameter-naming difference is fine if noted; a described component the code does not run, or a code path the paper does not describe, is not.
- Also check the opposite direction: anything in the code that affects predictions and is absent from the paper.
- Fix by editing the text or the code until both agree; never by changing a reported number.

Report

```
# Method-code alignment audit
Audited codebase: <path> (main entry: <file>)   Reference: method sections <x-y>

## Summary
| Dimension | Result |
|---|---|
| Specification violation | none found (spec_violation = false) |
| Method-code alignment | aligned (method_code_alignment = true) |

## Section by section
### 3.1 <Component> - ALIGNED
- Paper: <statement, formula>
- Code: <file:line> computes ... ✔
### 3.2 <Component> - DISCREPANCY
- Paper says ...; code does ...; resolution: <text fixed | code fixed>

## Code paths not described in the paper
- none | <list>

## Conclusion
<two sentences>
```
