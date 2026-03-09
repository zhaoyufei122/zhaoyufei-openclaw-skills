---
name: monitor-amuseables-aubergine
description: Monitor Jellycat Amuseables Aubergine stock and notify when availability changes. Use when the user wants to check or continuously watch the Jellycat Aubergine page, especially for page-level stock and small or large variant availability.
---

# Monitor Amuseables Aubergine

Use this skill to monitor the Jellycat Aubergine product page for stock changes.

## Scope

This skill currently targets one product page and tracks:
- page-level stock state
- small variant state when detectable
- large variant state when detectable
- anti-bot / challenge-page detection

## Default workflow

1. Use the shared Python environment `openclaw`.
2. Run a one-time check with the bundled script.
3. If the site returns an anti-bot challenge, report that clearly instead of pretending stock is unknown.
4. For continuous monitoring, run the script on an interval and notify only on changes unless the user asks otherwise.

## Files

- `jellycat_stock_skill.py` — main monitor script
- `requirements.txt` — Python dependencies
- `config.example.json` — example local config

## Output behavior

The script emits:
- `[CHANGE]` when stock changes relative to the previous state
- `[NO_CHANGE]` when stock is unchanged
- `[CHECK]` when `--always-notify` is used
- `[BLOCKED]` when the site returns an anti-bot or challenge page

## Notes

- State is stored locally in a JSON state file.
- This skill is specific to Jellycat Aubergine for now.
- Variant parsing depends on the site returning the real product page rather than an anti-bot interstitial.
