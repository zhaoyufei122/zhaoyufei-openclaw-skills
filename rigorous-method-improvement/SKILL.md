---
name: rigorous-method-improvement
description: Critic-gated research workflow (distilled from ScientistTwo, Google Cloud AI Research 2026) for improving a given method, baseline or SOTA on its own benchmark and backing the claim with evidence - limitation extraction, seed ideas with novelty check, subset-first experiments with Good/Bad/Engineer verdicts, idea evolution from execution traces, ablation-driven pruning, self-review with real rebuttal experiments, and a four-part integrity audit. Use whenever the user wants to beat, extend or improve a paper, baseline, model or codebase on a benchmark, test a research idea empirically, run ablations, write experimental results up as a paper or research report, or judge whether a claimed improvement is real - even when phrased casually ("make this model better", "try some ideas on this repo", "can we get a higher number than the paper", "is this gain legit").
---

# Rigorous Method Improvement

A workflow for the task "here is a method, its code and its benchmark; find a real improvement and prove it". It turns the research discipline of ScientistTwo into rules you can follow in one session, with or without subagents. It does not give you compute, data or an independent reviewer; it gives you the habits that make the result trustworthy.

What the discipline buys you, concretely: ideas aimed at diagnosed weaknesses instead of guesses; cheap failures (subset first); methods that keep only the parts that earn their place; a write-up whose claims survive an adversarial read; and code that matches the write-up.

## The one loop

Every stage below is the same shape. Hold it in mind and the rest is a table of what goes in each slot.

```
def stage(candidate, critic, refine, max_rounds):
    for _ in range(max_rounds):
        verdict, feedback = critic(candidate)
        if verdict == "accept": return candidate
        if verdict == "refine": candidate = refine(candidate, feedback)
        else:                   return None          # reject: discard
    return None                                      # budget spent: discard
```

Two rules make the loop worth running:

1. **The critic must not be the author defending its work.** If an Agent/subagent tool is available, run each critic in a fresh subagent that receives only the artifact (code, logs, report) and the critic question - never the generation transcript or the reasoning that led there. Without subagents, do the critic pass as a separate, explicit step: write the verdict and evidence first, using the rubric for that stage, before writing a single sentence of defense. A critic that only ever says "accept" is broken; if that happens, tighten the rubric.
2. **Budgets are real.** When a stage exhausts its rounds, the candidate is dropped, not nursed along. This is what stops a session from spending everything on the first idea. Defaults are in the budget table; the user can raise them.

## Stage map

| Stage | Candidate | Critic asks | Refine does | Budget |
|---|---|---|---|---|
| 0 Setup | Reproduced baseline on subset | Do numbers match the paper within tolerance? | Fix env/config, never the metric | 2 |
| 1 Limitations | List of limitation entries | Are these specific, mechanistic and sufficient to drive improvements? | Add missing limitations | 3 |
| 2 Seed ideas | Ranked idea list | Is it novel vs. the 2-3 closest papers? Does it target a limitation? | Add/replace ideas | - |
| 3 Subset experiment | Idea + code + subset results | Better than reproduced baseline? Good / Bad / Engineer | Engineering tuning only | 2 |
| 3b Full-set | Idea + code + full results | Better than the original paper's SOTA? | Engineering tuning only | 1 |
| 4 Evolve | New idea from traces | Same as stage 3 | Same | 3 rounds, stop at 2 Good |
| 5 Ablation | Best idea + component table | Is every component pulling weight? Is the gain attributable to the proposed mechanism? | Remove/replace components, re-verify | 1 |
| 6 Draft | Report/paper | - | - | - |
| 7 Self-review | Report | Score 1-10; what would a reviewer attack? | Run rebuttal experiments, revise | 2, stop at >= 7 |
| 8 Meta-review | Report + review | Does it meet the bar? Accept / Refine idea | Go back to stage 5 with the critique | 1 |
| Audit | Code + report | Four integrity checks (below) | Fix the code or the text, never the number | - |

## Stage 0 - Setup and reproduction

Before any idea: pin down what "better" means and what the baseline really scores on this machine.

- Read the paper/README and the code enough to answer: primary metric(s), datasets/splits, evaluation script, what the paper's headline numbers are, what hardware/time a full run needs.
- Define a **subset** that runs in minutes, not hours (fewer datasets, fewer seeds, fewer epochs, a slice of the data). Record exactly how it was derived.
- **Reproduce the baseline on the subset** and, if affordable, on the full set. Record paper number vs. reproduced number. All later comparisons are against the *reproduced* number on identical features/splits/seeds; the paper number is reported alongside for honesty.
- **Freeze the evaluator.** Copy or hash the metric code. Every "improvement" that comes from editing the evaluator, the threshold, or the test-time data path is a specification violation, not a result.
- Create the working tree (`python scripts/init_research.py research/ --evaluator <metric files>` does it and records the evaluator hashes):

```
research/
  STATUS.md              # current stage, budgets left, last verdict, stop reason, sham status
  00_setup.md            # metric, subset definition, baseline repro table, frozen evaluator hash, ε_abs / k
  01_limitations.md
  02_ideas.md
  03_experiments/<idea-slug>/{code/, logs/, report.md, verdict.md}
  04_ablation/{plans.md, report.md, redesign.md}
  05_draft.md            # or paper/ if LaTeX is requested
  06_review/round-<n>/{review.md, rebuttal-plan.md, rebuttal-report.md}
  07_audit/{reproducibility.md, spec-violation.md, references.md, method-code.md}
```

Every experiment script must be self-contained and print the numbers it reports, with a one-line "how to reproduce" (`cd ... && python final.py`). The reproducibility audit will re-run it later; write it so that re-run is trivial.

## Stage 1 - Limitations before ideas

Do not brainstorm. First diagnose. For each limitation write three fields (this is the template ScientistTwo's extractor uses and it forces specificity):

```
### N. <Short name of the flaw>
- Methodological flaw: what the method does, precisely (name the equation, the variable, the assumption).
- Why it limits the method: the mechanism by which this costs performance, and in which regime (near-OOD, long-tail, small data, high dim...).
- Opportunity for improvement: the family of changes that would address it (not yet a specific idea).
```

Critic question: *Would an expert reading only this list know where to attack?* Reject entries that are generic ("could use more data", "hyperparameters not tuned"), entries that describe the problem rather than the method, and entries with no mechanism. Aim for 3-6 entries; stop when the critic agrees the set is sufficient or the budget is spent.

## Stage 2 - Seed ideas with a novelty check

Generate one idea per limitation (or per group of limitations), then expand to 3-5 distinct candidates. For each:

```
## Idea: <name>
- Addresses limitations: #1, #3
- Core mechanism (2-4 sentences, with the key formula if any)
- What changes in the code (files/functions)
- Expected effect and on which metric/regime
- Novelty check: 2-3 closest existing works (search for them), and the one-sentence difference
- Cost: training-free / post-hoc / retrain; expected extra compute
```

Novelty check means actually searching, not asserting. If the closest work already does it, say so and either drop the idea or state the delta plainly. Rank by novelty and expected effect; the top 2 go to stage 3 first.

Prefer ideas that are mechanisms, not settings. Changing iteration counts, learning rates, label smoothing, activation functions or evaluation thresholds can move a number, but it is configuration tuning and it is not what this workflow is for (see "What counts" below).

## Stage 3 - Subset first, then full set

Implement the idea on a copy of the reproduced-baseline code. Run on the subset. Write `report.md` with: setup, the comparison table (ours vs. reproduced baseline vs. paper number, same cells), and a "how to reproduce" line.

The critic emits one of three verdicts into `verdict.md`:

- **Good** - consistently beats the reproduced baseline on the primary metric across the subset (not one lucky split). Proceed to full set.
- **Bad** - substantially worse, or the gain is inside noise. Discard; keep the log, it feeds stage 4.
- **Engineer** - the idea shows signal but needs tuning or a code fix (unstable training, obvious scale mismatch, wrong default). Allowed: hyperparameters of the *new* component, numerical fixes, bugs. Not allowed: touching the baseline's config in ways that would also help the baseline, or touching the evaluator. At most 2 engineering rounds; if still not Good, it is Bad.

**Noise floor (required before Good):**
- Run at least **3 seeds** on the subset (prefer 5 when a full-set run is cheap). A single seed never counts as a result.
- Let `Δ` be mean(ours) − mean(reproduced baseline) on the primary metric, and `σ` the seed standard deviation of the baseline (or pooled if both are re-seeded). Treat a gain as **inside noise** (hence Bad, not Good) if `|Δ| < max(ε_abs, k·σ)` with defaults `k = 1` and `ε_abs` set in `00_setup.md` from the metric's known precision (e.g. 0.1 pp for percentage points). Write both `Δ` and `σ` in `verdict.md`.
- "Consistently beats" means the win holds on a majority of seeds and the mean clears the floor above — not that every seed wins.

Only Good ideas run on the full set. Full-set critic compares against the *original paper's* numbers as well; an idea that beats your reproduction but not the paper is reported as such, not spun.

Run the **specification-violation filter** right after each experiment, while the code is fresh (checklist in the audit section). A result that fails it is discarded immediately, however good the number looks.

## Stage 3c - Sham / negative control (optional but recommended)

Before promoting the first Good idea to full-set, run one **sham** on the same subset and seeds: a change that should not help (random weight noise at a tiny scale, shuffled feature channel, or a no-op toggle that still recompiles the pipeline). Record it under `03_experiments/sham-*/`.

- If the sham also clears the noise floor, the evaluator or split is leaky or under-powered: fix the setup before trusting any Good idea.
- If the sham stays inside noise while the candidate clears it, note that in `STATUS.md` and proceed.
- Skip only when the user forbids extra runs; then write `sham: skipped (user)` in `STATUS.md`.

## Stage 4 - Evolve from traces, keep exploring

After the first round, feed *all* traces so far - successes and failures, with their logs and critic feedback - into idea evolution. Failure logs are the most informative input: "HSKP weights collapsed to near-uniform" tells you more than any success does. Produce evolved ideas that explain what they learned from which trace.

Each round evaluates two candidates: one evolved idea and one still-unevaluated seed idea (next in the novelty ranking). This keeps the search from collapsing onto the first thing that half-worked. Stop when 2 ideas are Good on the full set or after 3 rounds. If zero ideas are Good after the budget, stop the whole workflow and report that honestly with the traces; that is a valid outcome.

Select the best Good idea by full-set metrics plus the logs (stability, cost, breadth across datasets), and say why.

## Stage 5 - Ablation as pruning, not decoration

The purpose of ablation here is to find out which parts of the method are real. Plan one ablation per component plus one for the most sensitive hyperparameter; hold everything else identical to the main run, state that explicitly, and re-use cached features/checkpoints so the comparison is exact.

Then the critic reads the ablation table and asks, for each component: *does removing it hurt?* Components that contribute nothing, or hurt, are **removed**, and the simplified method is re-run on the full set. The method is only accepted when the comparison agent confirms the refined version is at least as good as the previous best; otherwise keep the previous best.

Write `redesign.md` as a table:

```
| # | Ablation finding                               | Redesign                                      |
|---|------------------------------------------------|-----------------------------------------------|
| 1 | Layer weights collapsed to near-uniform (0.11-0.13) | Replace with class-aware Fisher weighting    |
| 2 | Orthogonal alignment gave +0.01%               | Removed - features blended directly           |
| 3 | Feature-level gating wrecked near-OOD          | Moved gate to score level, asymmetric min(0,z)|
```

A method that started with five components and ends with two is a success of this stage, not a failure. The ablation critic also has a second question: *is the gain attributable to the proposed mechanism?* If the ablation shows the gain came from something incidental (an optimizer change, a regularizer added along the way, a different evaluation split), the contribution is rejected even though the number is higher.

## Stage 6 - Draft

Write the report in paper structure (abstract, intro with the limitations, method, experiments with main table + ablations + insight/limitation analysis, conclusion). Markdown by default; LaTeX only if asked. Every number in the text must appear in a table that a script produced. Report per-dataset and average, wins/ties/losses where applicable, and the paper's number next to the reproduced one.

Citations: cite only works you have found and can identify (title, authors, venue/year). Keep a list of what each citation was verified against; the reference audit uses it.

## Stage 7 - Self-review with real rebuttal

Review the draft as a critic (subagent if possible, otherwise the separate-step rule) on the ICLR 1-10 scale, with sections Summary / Strengths / Weaknesses (W1..) / Questions (Q1..) / Score / Confidence. Weaknesses must be the kind a real reviewer writes: missing baseline, single-backbone evidence, gain inside seed variance, unexplained hyperparameter, claim not supported by a table.

If the score is below 7, write `rebuttal-plan.md`: for each W/Q, the *experiment* that would answer it (not the sentence). Run the experiments. Write `rebuttal-report.md` in the shape:

```
# Rebuttal - <what it tests>
- Reviewer concern addressed: W2 / Q1
- Setup: backbone, datasets, seeds, caps, metrics, reproduce command
## Summary
- Metric A: baseline -> ours (delta); win/tie/loss at |delta| > noise floor
- Conclusion: what this does and does not establish
```

Then revise the draft with the new evidence and re-review. Two rounds maximum. A rebuttal that changes only wording is not a rebuttal.

Write the conclusion of each rebuttal honestly: "gains are real on regression, parity on classification" is a better sentence than an overstated uniform win, and a meta-reviewer will check.

## Stage 8 - Meta-review

One final pass over draft + review: Accept, or Refine with a critical weakness named. On Refine, go back to stage 5 with the critique as input (refine the idea, re-ablate, re-draft, re-review), at most once. If the refined idea does not strictly beat the previous best, keep the previous best and stop.

## Integrity audit - four checks, done when they are cheapest

These are what make an automated research result credible. Run them as the artifact exists, not at the end.

1. **Score verification** (after each full-set run, and again at the end): a fresh process re-runs the reported script and the numbers match exactly or within stated tolerance. If cached artifacts are involved, re-derive at least one from scratch and compare. Write `reproducibility.md` with a verdict line, what was re-run, and the numbers side by side.
2. **Specification compliance** (right after each experiment): checklist - no test/OOD/validation data reaches any fitted statistic, threshold or calibration; no hardcoded answers or dataset-specific constants; evaluator untouched (hash matches stage 0); baseline computed from the same features/splits/seeds as ours; seeds fixed, no per-dataset hyperparameter search unless the baseline got the same. Any violation discards the result.
3. **Reference verification** (at drafting): every citation resolves to a real work you located. Remove or replace any you cannot.
4. **Method-code alignment** (at the end): section by section, paper statement vs. the code lines that implement it, with file:line references, each marked ALIGNED or with the discrepancy. Fix the text or the code so they agree; never leave a described component that the code does not run, or a code path the paper does not mention.

## What counts as a contribution

This workflow holds itself to a stricter standard than "the number went up":

- The gain must survive ablation and be attributable to the proposed mechanism.
- Configuration-level edits (iteration counts, precision, activations, label smoothing, an evaluator threshold) are not contributions, even when they move the metric more than a real mechanism does. Report them, if found, as tuning observations, separately.
- A gain that lives in the evaluator or in the data path is a specification violation.
- A gain on one split or one seed is a hypothesis, not a result.
- "No Good idea found" with a clean trace of what was tried and why it failed is an acceptable, reportable outcome.

## Budget defaults

| Knob | Paper (ScientistTwo) | Default here |
|---|---|---|
| Limitation extraction rounds | 16 | 3 |
| Seed ideas generated | pool, top-N0 evaluated | 3-5, top-2 first |
| Candidates per evolution round | 2 (1 evolved + 1 seed) | 2 |
| Evolution rounds / early stop | 4 / 4 Good | 3 / 2 Good |
| Engineering rounds per idea | 2 | 2 |
| Ablation-driven refinement | 1 | 1 |
| Review rounds / accept threshold | 2 / score >= 8 | 2 / score >= 7 |
| Review-driven idea refinement | 1 | 1 |

Scale up when the user has the compute and asks; scale down when a single full-set run costs hours - then do more on the subset and say so in the report.

## Running this in a session

- Start by writing `00_setup.md` and a task list with one item per stage; tick them as you go so a returning user sees where things are.
- Keep `research/STATUS.md` current after every stage: current stage, budget remaining, last verdict, stop reason (if any), sham status. Resume from `STATUS.md` + the newest artifact, not from chat memory.
- Each stage ends with a written artifact in `research/`. If the session dies, the next one resumes from the files, not from memory.
- When something is expensive to redo and ambiguous (which metric is primary, whether retraining is allowed, how much compute may be spent), ask before running. Otherwise take the most reasonable reading, write it in `00_setup.md`, and continue.
- Report at the end: the final method in one paragraph, the main table, what was pruned and why, the audit verdicts, the honest limitations, and the traces of what failed.

## Bundled files

Read these when you reach the stage that needs them; SKILL.md alone is enough to run the loop.

- `references/templates.md` - fill-in templates for every artifact: limitation entry, idea card, experiment report and verdict, ablation plan and redesign table, review (with the 1-10 rubric), rebuttal plan and report, final summary.
- `references/integrity-audit.md` - the four audits as checklists plus the report formats they should produce.
- `scripts/init_research.py` - creates the `research/` tree with stub files and hashes the evaluator files you name.
