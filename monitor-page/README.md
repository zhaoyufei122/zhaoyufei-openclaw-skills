# monitor-page

Page-based stock monitoring skill.

## Current target

- Jellycat Aubergine product page
- Large variant focus, Small variant also tracked

## Run

```bash
pip install -r requirements.txt
python jellycat_stock_skill.py --once
python jellycat_stock_skill.py --interval 300
```

## Optional webhook

```bash
python jellycat_stock_skill.py --interval 300 --webhook-url "https://your-webhook-url"
```

## Notes

This is a page-polling stock checker. It stores local state in `.jellycat_aubergine_state.json` and emits change notifications when stock state changes.
