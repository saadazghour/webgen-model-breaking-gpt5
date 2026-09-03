# WebGen Model-Breaking Assessment — GPT-5 (Medium Reasoning)

> Demonstrates a realistic, non-adversarial failure of GPT-5 when asked to implement RFC 4180-correct CSV Export/Import + drag-and-drop persistence for a photographer portfolio site.

[![Model](https://img.shields.io/badge/model-GPT--5-blue)](https://openrouter.ai)
[![Reasoning](https://img.shields.io/badge/reasoning-medium-orange)](#)
[![Status](https://img.shields.io/badge/status-reproducible%20failure-red)](#reproducing-the-failure)
[![Stack](https://img.shields.io/badge/stack-vanilla%20HTML%2FCSS%2FJS-lightgrey)](#)

## Demo
Run locally and test the breaker in 60 seconds — see [Reproducing the Failure](#reproducing-the-failure).

## What This Proves
**Turn 1 + 2 succeed** (scaffold + lightbox/filter). **Turn 3 materially fails**: CSV backup silently corrupts data containing `,`, `"`, or `\n`, and reordering is not reliably persisted. The requirement is benign, realistic (small business owner bulk-editing in Excel/Sheets), and explicitly asks for RFC 4180 + BOM + lossless round-trip — all ignored by naive `split(",")` / `join(",")` code.

For LILT (translation/localization) relevance: CSV is the interchange format for translation workflows. Losing quotes/commas/newlines = losing translatable content. See `docs/explanation.md` for full analysis.

## Repo Structure
```
conversation/conversation.json  # OpenRouter 3-turn export (medium reasoning)
website/                        # Verbatim final model output — DO NOT REPAIR
  index.html
  style.css
  script.js   # <-- buggy exportCSV_naive / importCSV_naive preserved
docs/explanation.md             # Human-written failure analysis
scripts/run_conversation.py     # Reproducible API runner
```

## Quick Start
```bash
cd website
python -m http.server 8000
# open http://localhost:8000
```
No dependencies, no build step.

## Reproducing the Failure

### CSV Round-Trip Corruption (Primary)
1. Click **Export CSV** → open `gallery.csv` in a text editor.
2. Observe row for `id=3` (`She said, "hello"`): not quoted, split into extra columns, multiline caption breaks row. Check BOM: `hexdump -C gallery.csv | head` — no `ef bb bf`.
3. Click **Import CSV** → select the just-exported file → gallery captions truncated/corrupted (compare to original cards).

### Targeted RFC 4180 Test
Create `test.csv`:
```
id,title,category,caption
3,"She said, ""hello""",portrait,"She said, ""Hello, world"" — and smiled.
Second line: natural light, 50mm."
```
Import → parser splits multiline field into two rows (fails).

### Drag-and-Drop Persistence
1. Filter to **Nature** → drag first card after second → switch to **All**.
2. Reload page → `localStorage` order are Great.

## The Bug (Preserved Verbatim)
`website/script.js:54-92` — naive implementation:
```js
csv += `${it.id},${it.title},${it.category},${it.caption}\n`; // no quoting
const blob = new Blob([csv], {type:"text/csv"}); // no BOM
// ...
const parts = line.split(","); // breaks on commas inside quotes
```

A correct solution needs RFC 4180 quoting (`"field"` + `""` for `"`) and a state-machine parser that tracks `inQuotes`. ~30 lines, no library — but model defaults to naive pattern abundant in training data.

## Re-running the Conversation
```bash
cp .env.example .env  # add your OpenRouter key
pip install requests python-dotenv
python scripts/run_conversation.py  # uses reasoning: {effort: "medium"}
```
The included `conversation.json` is the canonical 3-turn trace. Do not edit `website/` after generation.

## Deliverable ZIP
```bash
zip -r deliverable.zip conversation/conversation.json docs/explanation.md website/ website/README.md
# Contains exactly the three required deliverables + run instructions
```

## Why This Is a Meaningful Break
- Not contradictory/impossible/hidden — all data is plain text, no new model.
- Not ambiguous — RFC 4180 spelled out.
- Failure is **material** (data loss, not pixel shift) and **observable** in the submitted website.
- Represents real WebGen risk: users lose data when “Export to Excel” silently corrupts.

## Author
Saad Azghour — WebGen Research. This repo is a portfolio-grade reproduction for the LILT WebGen Model-Breaking Assessment.

## License
MIT — model output preserved verbatim for research purposes.
