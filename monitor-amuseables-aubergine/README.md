# monitor-amuseables-aubergine

Monitor Jellycat Amuseables Aubergine stock.

## Environment

Use the shared conda environment:

- `openclaw`

Python path on this machine:

- `C:\Users\46659\.conda\envs\openclaw\python.exe`

## Run once

```bash
python jellycat_stock_skill.py --once
```

## Continuous monitoring

```bash
python jellycat_stock_skill.py --interval 300
```

## Notes

This script now detects Cloudflare / anti-bot challenge pages and reports them as blocked instead of silently treating them as unknown stock.
