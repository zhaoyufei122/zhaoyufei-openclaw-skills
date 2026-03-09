---
name: monitor-page
description: Monitor a product page for stock changes and notify when availability changes. Use when the user wants page-based restock monitoring, especially for Jellycat product pages or other simple e-commerce product pages with small and large variants.
---

# Monitor Page

Use this skill to monitor a product page for stock changes.

## Scope

This skill is currently built around a Jellycat product page monitor and tracks:
- page-level stock state
- small variant state
- large variant state

## Default workflow

1. Install Python dependencies from `requirements.txt`.
2. Run a one-time check with `python jellycat_stock_skill.py --once`.
3. For continuous monitoring, run `python jellycat_stock_skill.py --interval 300`.
4. If the user wants remote notifications, pass `--webhook-url`.

## Files

- `jellycat_stock_skill.py` — main monitor script
- `requirements.txt` — Python dependencies
- `config.example.json` — example local config

## Output behavior

The script emits:
- `[CHANGE]` when stock changes relative to the previous state
- `[NO_CHANGE]` when stock is unchanged
- `[CHECK]` when `--always-notify` is used

## Notes

- State is stored locally in `.jellycat_aubergine_state.json` by default.
- This skill is currently best suited for simple page polling and stock-state parsing.
- If Python is unavailable, treat the skill as installed-but-not-runnable until Python is added.
