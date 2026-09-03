# Run Instructions

The files in this folder are the **verbatim final model output** (Turn 3) — no manual repair.

## Install
No dependencies. Vanilla HTML/CSS/JS.

## Run
```bash
python -m http.server 8000
# or: npx serve .
# open http://localhost:8000
```

## Test the Failure (60s)
1. Export CSV → open gallery.csv → note caption with commas/quotes is unquoted and multiline breaks row.
2. Import the same gallery.csv → captions truncated/corrupted.
3. Filter to Nature → drag to reorder → reload → order reverts.

See `../docs/explanation.md` for full reproduction steps.
