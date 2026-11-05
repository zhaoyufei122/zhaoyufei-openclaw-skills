# Templates

Fill-in formats for every artifact the workflow produces. Each one mirrors what ScientistTwo's agents actually emit (paper arXiv:2609.19644, Appendix C), trimmed to the fields that carry information. Copy the block, fill it, save it at the path named in SKILL.md.

Contents

1. `00_setup.md` - setup and baseline reproduction
2. Limitation entry
3. Idea card
4. Experiment report and verdict
5. Ablation plan, ablation report, redesign table
6. Review (with the 1-10 rubric)
7. Rebuttal plan and rebuttal report
8. Meta-review
9. Final summary

---

## 1. `00_setup.md`

```
# Setup

## Problem
- Source paper / repo:
- Task in one sentence:
- Primary metric(s) and direction (higher/lower is better):
- Secondary metrics:
- Datasets / splits used by the paper:

## Subset (for fast iteration)
- Definition (which datasets, seeds, epochs, fraction):
- Why it is representative:
- Wall-clock per run:

## Baseline reproduction
| Setting | Paper | Reproduced (subset) | Reproduced (full) |
|---|---|---|---|
| <metric on dataset A> | | | |
| Average | | | |
- Tolerance accepted and why:
- Discrepancies and their likely cause:

## Noise floor
- ε_abs (absolute floor on primary metric):
- k (multiplier on seed σ; default 1):
- Min seeds on subset (default 3):

## Frozen evaluator
- Files: <path> sha256 <hash>
- Rule: these files are never edited; any metric change is a specification violation.

## Decisions taken without asking (if working unattended)
-
```

## 2. Limitation entry (`01_limitations.md`)

```
### N. <Short name of the flaw>
- Methodological flaw: what the method does, precisely. Name the equation, variable or assumption.
- Why it limits the method: the mechanism by which this costs performance, and in which regime.
- Opportunity for improvement: the family of changes that would address it (not yet a specific idea).
```

Critic check for the list as a whole: specific (names a mechanism, not "could be better"), about the *method* (not the problem or the dataset), sufficient (an expert would know where to attack), 3-6 entries.

Example of a passing entry:

```
### 1. Total variance as a weighting proxy lacks class-separability awareness
- Methodological flaw: the layer weight a_l is computed from total feature variance Tr(A_l^T A_l) over
  all training samples; it ignores label information entirely.
- Why it limits the method: a layer with noisy, non-discriminative activations that happen to have large
  magnitude is weighted heavily, corrupting the blended feature space with irrelevant signal.
- Opportunity for improvement: replace total variance with a class-aware criterion (between/within-class
  variance ratio, Fisher discriminability, mutual information with labels).
```

## 3. Idea card (`02_ideas.md`)

```
## Idea <k>: <name>
- Addresses limitations: #
- Core mechanism (2-4 sentences, key formula if any):
- What changes in the code (files / functions):
- Expected effect, on which metric and regime:
- Novelty check: closest works found by search (title, year) and the one-sentence difference:
- Cost: training-free / post-hoc / retrain; extra compute:
- Novelty rank:
```

## 4. Experiment report and verdict (`03_experiments/<idea>/`)

`report.md`

```
# <Idea name> - <subset | full> results

## Setup
- Data / splits / seeds (identical to baseline reproduction):
- Backbone / checkpoint reused:
- What differs from baseline code (one line per change):

## Results
| Dataset | Ours | Baseline (reproduced) | Baseline (paper) |
|---|---|---|---|
| ... | | | |
| Average | | | |
Each cell: <metric A> / <metric B>; direction.

## Observations
- Where the gain is / is not (near-OOD vs far-OOD, small vs large datasets, ...):
- Anything that looked wrong in the logs:

## How to reproduce
cd <dir> && python <script>.py
```

`verdict.md` (written by the critic, before any defense)

```
Verdict: Good | Bad | Engineer
Evidence:
- <metric> on <n>/<N> datasets improved by <x> (noise floor <y>)
- ...
If Engineer - what to change (new-component hyperparameters, numerical fixes, bugs only):
-
If Bad - lesson for idea evolution:
-
Spec-violation filter run: yes / no - findings:
```

## 5. Ablation (`04_ablation/`)

`plans.md`

```
| # | Ablated component | Variant(s) | Held identical | Expected if component is real |
|---|---|---|---|---|
| 1 | Layer weighting w_l | uniform; trace-only (baseline); proposed; proposed with gamma in {..} | everything else | drop on near-OOD |
```

`report.md`: same table shape as the experiment report, one row per variant, plus a "Key insights" list with one line per component saying *contributes / neutral / harmful* with the number.

`redesign.md`

```
| # | Ablation finding | Redesign |
|---|---|---|
| 1 | <component> gave +0.01% | Removed |
| 2 | <component> collapsed to <degenerate behaviour> | Replaced by <...> |
| 3 | <component> hurt <regime> | Moved to <...> |
Re-run of simplified method on full set: <avg before> -> <avg after>; accepted / rejected because ...
Attribution check: the remaining gain is explained by <mechanism>, not by <incidental change>.
```

## 6. Review (`06_review/round-<n>/review.md`)

```
# Review - round <n>

## Summary (what the paper claims, in the reviewer's words)

## Strengths
- S1.
## Weaknesses
- W1. <specific, checkable, tied to a table or its absence>
- W2.
## Questions
- Q1.

## Scores
- Soundness (1-4):
- Presentation (1-4):
- Contribution (1-4):
- Rating (1-10):
- Confidence (1-5):
```

Rating scale (ICLR convention): 1 strong reject · 3 reject, not good enough · 5 marginally below threshold · 6 marginally above threshold · 8 accept, good paper · 10 strong accept, should be highlighted. Threshold in this workflow: 7.

What the reviewer must actually check before scoring:
- every numeric claim in the text appears in a table produced by a script;
- the baseline is reproduced on the same features/splits/seeds, and the paper's number is shown too;
- variance (seeds) or a noise floor is reported, and the gain exceeds it;
- ablations exist for every component and the surviving components all contribute;
- the novelty delta against the closest works is stated and is true;
- limitations are stated and are the real ones.

Weaknesses that only say "more experiments would help" are not acceptable; name the experiment.

## 7. Rebuttal (`06_review/round-<n>/`)

`rebuttal-plan.md`

```
| Concern | Experiment that answers it | Cost | Decision rule |
|---|---|---|---|
| W2: single backbone | re-run on <backbone 2>, same datasets/seeds | ~1h | gain holds on >= half of datasets |
```

`rebuttal-report.md`

```
# Rebuttal - <what it tests>
- Reviewer concern addressed: W2 / Q1
- Setup: backbone, datasets, seeds, caps, metrics, reproduce command
- Method (unchanged from the draft unless stated):

## Summary
- <metric>: baseline -> ours (delta); win / tie / loss at |delta| > <noise floor>: a / b / c
- Conclusion: what this establishes and what it does not.

## Full table
| Dataset | Baseline | Ours | Delta | Selected config |
```

Write the conclusion so a meta-reviewer could not accuse it of overstating: name the regime where the gain holds and the regime where it is parity.

## 8. Meta-review (`06_review/meta.md`)

```
Decision: Accept | Refine
Critical weakness (if Refine): <one named algorithmic or empirical weakness>
Guidance for idea refinement:
```

## 9. Final summary (end of session)

```
# Result
- Final method (one paragraph):
- Main table (ours vs reproduced vs paper):
- What was pruned by ablation and why:
- Audit verdicts: score verification / specification / references / method-code:
- Honest limitations:
- Traces of what failed (idea -> why -> lesson):
- Compute spent:
```
