#!/usr/bin/env python3
import json, pathlib, sys, zipfile, re

REPO = pathlib.Path(__file__).resolve().parents[1]
ok = True
def check(cond, msg):
    global ok
    print(("✓" if cond else "✗") + " " + msg)
    if not cond: ok=False
    return cond

print("=== 1) File Structure ===")
check((REPO/"conversation/conversation.json").exists(), "conversation/conversation.json exists")
check((REPO/"docs/explanation.md").exists(), "docs/explanation.md exists")
check((REPO/"website/index.html").exists(), "website/index.html exists")
check((REPO/"website/style.css").exists(), "website/style.css exists")
check((REPO/"website/script.js").exists(), "website/script.js exists")
check((REPO/"website/README.md").exists(), "website/README.md exists")
check((REPO/"deliverable.zip").exists(), "deliverable.zip exists")
check(not (REPO/".env").exists() or "sk-or" not in (REPO/".env").read_text(errors="ignore"), ".env not leak key")
check((REPO/".gitignore").exists(), ".gitignore exists")

print("\n=== 2) conversation.json ===")
try:
    j = json.loads((REPO/"conversation/conversation.json").read_text())
    check(j.get("model")=="openai/gpt-5", f'model is openai/gpt-5 (got {j.get("model")})')
    check(j.get("generation_settings",{}).get("reasoning",{}).get("effort")=="medium", "reasoning.effort == medium")
    msgs = j.get("messages",[])
    check(len(msgs)==6, f"6 messages (3 turns) — got {len(msgs)}")
    if len(msgs)==6:
        check(all(msgs[i]["role"]=="user" for i in [0,2,4]), "user turns at 0,2,4")
        check(all(msgs[i]["role"]=="assistant" for i in [1,3,5]), "assistant turns at 1,3,5")
        all_text = " ".join(m["content"] for m in msgs).lower()
        check("alex rivera" in all_text or "gallery" in all_text, "same website topic across turns (gallery/portfolio)")
        check("rfc 4180" in msgs[4]["content"].lower() or "rfc4180" in msgs[4]["content"].lower(), "Turn 3 mentions RFC4180")
        check("bom" in msgs[4]["content"].lower(), "Turn 3 mentions BOM")
        check("drag" in msgs[4]["content"].lower() and "localstorage" in msgs[4]["content"].lower(), "Turn 3 mentions drag+localStorage")
    # OpenRouter format hint
    check("openrouter" in json.dumps(j).lower() or j.get("model","").startswith("openai/"), "OpenRouter-style model id")
except Exception as e:
    check(False, f"conversation.json valid JSON — {e}")

print("\n=== 3) Website ===")
html = (REPO/"website/index.html").read_text(errors="ignore") if (REPO/"website/index.html").exists() else ""
js = (REPO/"website/script.js").read_text(errors="ignore") if (REPO/"website/script.js").exists() else ""
check("<title>" in html and "Alex Rivera" in html, "index.html has title Alex Rivera")
check('id="galleryGrid"' in html, "gallery grid exists")
check('id="exportBtn"' in html, "Export CSV button exists")
check('id="importFile"' in html, "Import CSV input exists")
check("exportCSV_naive" in js or "exportCSV" in js, "export function present")
check('split(",")' in js or "split(',')" in js, "naive split present (proves intentional failure)")
check('Blob' in js, "Blob download present")
# Correct would have FEFF BOM — naive does not
check(chr(0xFEFF) not in js or 'Blob([csv]' in js, "Export likely missing BOM (expected failure)")
# Drag
check("draggable" in html or "draggable" in js, "draggable present")
check("localStorage" in js, "localStorage persistence present")
check("picsum.photos" in html or "picsum.photos" in js, "placeholder images use picsum")

print("\n=== 4) explanation.md ===")
exp = (REPO/"docs/explanation.md").read_text(errors="ignore") if (REPO/"docs/explanation.md").exists() else ""
checks = [
    ("Website" in exp, "has Website section"),
    ("Turn 1" in exp, "mentions Turn 1"),
    ("Turn 3" in exp, "mentions Turn 3"),
    ("Expected" in exp and "Actual" in exp, "has Expected vs Actual"),
    ("Reproduce" in exp or "Reproduction" in exp, "has reproduction steps"),
    ("RFC" in exp, "mentions RFC4180"),
    ("localStorage" in exp or "localstorage" in exp.lower(), "mentions localStorage"),
    ("verbatim" in exp.lower() or "not repaired" in exp.lower(), "mentions verbatim preservation"),
    (len(exp) > 2000, f"length >2000 chars (got {len(exp)}) — not generic filler"),
]
for c,m in checks: check(c,m)
# Anti-AI filler hint
check("as an ai" not in exp.lower(), "no generic AI filler")

print("\n=== 5) deliverable.zip ===")
try:
    z = zipfile.ZipFile(REPO/"deliverable.zip")
    names = z.namelist()
    check("conversation/conversation.json" in names, "ZIP has conversation.json")
    check("docs/explanation.md" in names, "ZIP has explanation.md")
    check(any(n.startswith("website/") for n in names), "ZIP has website/")
    check(any(".env" in n for n in names)==False, "ZIP does NOT leak .env")
    check(len(names)>=5, f"ZIP has >=5 entries (got {len(names)})")
    # Check README inside website/
    check("website/README.md" in names, "ZIP has website/README.md (run instructions)")
except Exception as e:
    check(False, f"ZIP readable — {e}")

print("\n=== 6) Git ===")
check((REPO/".git").exists(), ".git exists")
# quick log check
import subprocess
try:
    log = subprocess.check_output(["git","log","--oneline"], cwd=REPO, text=True)
    check("model-breaking" in log.lower() or "webgen" in log.lower(), "git log has commit")
except: check(False, "git log readable")

print("\n" + ("="*50))
if ok:
    print("ALL CHECKS PASSED — ready to submit")
    sys.exit(0)
else:
    print("SOME CHECKS FAILED — fix above before submitting")
    sys.exit(1)
