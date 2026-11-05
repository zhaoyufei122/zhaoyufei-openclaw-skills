# rigorous-method-improvement

A skill for AI coding agents that turns "here is a method, its code and its benchmark — make it better" into a disciplined research loop with evidence at every step.

It distils the methodology of **ScientistTwo** (Google Cloud AI Research, 2026, [arXiv:2609.19644](https://arxiv.org/abs/2609.19644)) — limitation-driven ideation, subset-first experiments, idea evolution from execution traces, ablation-driven pruning, simulated peer review with real rebuttal experiments, and a four-part integrity audit — into instructions an agent can follow in a single session. It does **not** reproduce the ScientistTwo system (which runs for days on real GPUs with separately trained reviewer models); it reproduces its *habits*.

**Made by Yufei Zhao.** Methodology credit belongs to the ScientistTwo paper; this repository is an independent distillation and is not affiliated with the paper authors.

## What the agent does with it

1. Reproduces the baseline on a fast subset and freezes the evaluator.
2. Extracts specific, mechanistic limitations of the baseline before proposing anything.
3. Generates seed ideas that target those limitations, with a real novelty search.
4. Tests ideas on the subset first; a critic labels each **Good / Bad / Engineer** with a bounded tuning budget and an explicit noise floor.
5. Optionally runs a sham / random-change negative control so accidental gains are visible.
6. Evolves new ideas from the logs of successes *and* failures, while still exploring unevaluated seeds.
7. Ablates the best idea and **removes** every component that does not earn its place.
8. Writes the result up in paper structure, reviews it as a hostile reviewer, and answers weaknesses with experiments rather than wording.
9. Audits the outcome: numbers reproduce, no reward hacking, no hallucinated citations, code matches the text.

Every stage is the same `candidate -> critic -> refine` loop with a round budget, and every stage leaves a file in a `research/` tree (plus `STATUS.md`) so a session can be resumed from disk.

## Layout

```
rigorous-method-improvement/
├── SKILL.md                      # the skill: workflow, stage map, rules, budgets
├── references/
│   ├── templates.md              # fill-in templates for every artifact
│   └── integrity-audit.md        # the four audits as checklists + report formats
├── scripts/
│   └── init_research.py          # creates the research/ tree, STATUS.md, hashes evaluator files
├── examples/
│   └── prompts.md                # prompts that should / should not trigger the skill
├── LICENSE
└── README.md
```

## Install

Copy the `rigorous-method-improvement/` folder into whatever skill directory your agent loads:

- **Cursor / Grok Bot**: project skills under `.cursor/skills/` or your agent skill store
- **OpenClaw**: `~/.openclaw/skills/` or the workspace `skills/` directory
- **Other agents**: any framework that reads `SKILL.md` with YAML frontmatter (`name`, `description`)

Example:

```text
~/.openclaw/skills/
  rigorous-method-improvement/
    SKILL.md
    references/
    scripts/
    examples/
```

## Using it

Point the agent at a paper/repo and a benchmark and ask for an improvement, e.g.

> Here is the X-Maha OOD detection repo and the CIFAR-100 benchmark it reports on. Find a method that beats it and write it up so I could submit it.

The agent will create `research/`, work through the stages, keep `STATUS.md` current, and end with a final summary: the method, the main table (ours vs. reproduced baseline vs. paper), what ablation pruned, the audit verdicts, and the traces of what failed.

Budgets are deliberately smaller than the paper's (see the table in `SKILL.md`); raise them when you have the compute.

## What this skill will not do

- Supply compute, data or a reproducible baseline environment. Reproduction is the slowest step and the skill can only insist on it.
- Provide an independent reviewer. A single model reviewing its own draft is biased; the skill mitigates this by running critics in fresh subagent contexts where available and by requiring that every weakness be answered with an experiment, not a sentence.
- Guarantee a gain. "No Good idea found, here is what was tried and why it failed" is an explicitly valid outcome.

## Credit

- **Author:** Yufei Zhao (Made by myself)
- **Methodology source:** *ScientistTwo: Pioneering the Human Knowledge Frontier with Autonomous AI*, Google Cloud AI Research, arXiv:2609.19644 (2026). The templates in `references/` follow the shape of the artifacts shown in that paper's Appendix C.
- This repository is an independent distillation and is not affiliated with the paper authors.

## License

MIT — see `LICENSE`.

---

## 中文说明

这是一个给 AI 编程 agent 用的 skill，把 ScientistTwo（Google Cloud AI Research，2026）论文中的科研方法论提炼成可执行的工作流：先找 baseline 的局限，再针对局限提想法并做新颖性检索；先在小子集上实验，critic 给出 Good / Bad / 需要工程调优三种判定，并带明确噪声底；可用 sham 负对照防假阳性；用成功与失败的执行日志演化新想法；对最优想法做消融并砍掉无贡献的组件；按论文结构写报告，自审后用补充实验回应弱点；最后做四项完整性审计。`research/STATUS.md` 记录当前阶段与预算，方便断点续跑。

**作者：Yufei Zhao（Made by myself）。** 不提供算力、数据或独立评审器，只提供让结果可信的纪律。安装方式见上文 Install 一节。
