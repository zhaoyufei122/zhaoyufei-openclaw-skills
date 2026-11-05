# zhaoyufei-openclaw-skills

Custom OpenClaw skills for personal assistant workflows.

## Included skills

- `mail-monitor` — IMAP-based inbox reading and triage for Gmail and 163 mail.
- `monitor-amuseables-aubergine` — Jellycat Amuseables Aubergine stock monitoring skill.
- `rigorous-method-improvement` — research-method improvement skill distilled from ScientistTwo habits.

## Install

Clone or copy this repository, then place the skill folder into one of these OpenClaw skill locations:

- `~/.openclaw/skills/`
- your workspace `skills/` directory

Example target layout:

```text
~/.openclaw/skills/
  mail-monitor/
    SKILL.md
    package.json
    scripts/
    references/
```

## Per-skill setup

See each skill folder for runtime details. For `mail-monitor`:

1. Run `npm install` inside `mail-monitor/`
2. Configure mailbox environment variables locally
3. Keep secrets local; do not commit real credentials

## Security

This repository is intended to contain reusable skill code only.

Do not commit:
- mailbox passwords
- app passwords
- authorization codes
- personal OpenClaw config files
- private memory files
