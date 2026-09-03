#!/usr/bin/env python3
"""
Run the 3-turn WebGen assessment conversation via OpenRouter API
with medium reasoning and save to conversation/conversation.json

Usage:
  echo 'OPENROUTER_API_KEY=sk-or-v1-...' > .env
  pip install requests python-dotenv
  python scripts/run_conversation.py

Set MODEL to whatever OpenRouter lists for GPT-5 (e.g. openai/gpt-5 or openai/gpt-5-chat)
"""
import os, json, sys, time
from pathlib import Path

try:
    import requests
    from dotenv import load_dotenv
except ImportError:
    print("pip install requests python-dotenv")
    sys.exit(1)

load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-5")
API_URL = "https://openrouter.ai/api/v1/chat/completions"

if not API_KEY:
    print("Missing OPENROUTER_API_KEY in .env — using mock save mode (no API call).")
    print("Create .env from .env.example and rerun to do live calls.")
    # Still write a placeholder that matches exported conversation.json
    sys.exit(0)

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://github.com/saadazghour/webgen-model-breaking-gpt5",
    "X-Title": "WebGen Model-Breaking Assessment",
}

TURNS = [
    "Build a responsive personal portfolio website for freelance photographer Alex Rivera using vanilla HTML/CSS/JS. Include a hero section with name and tagline, an About section, a gallery grid with 6 placeholder images, and a contact form (frontend only, no backend). Use a clean minimal design, mobile-responsive, and keep all code in separate index.html, style.css, script.js files. Return the complete runnable code.",
    "Great. Now add two improvements to the same site: 1) A lightbox when clicking any gallery image — show large image with title and caption, with Next/Previous buttons and close on overlay click. 2) Category filtering with buttons All / Nature / Urban / Portrait and smooth filtering of the gallery. Keep the design consistent and update the existing files.",
    "Perfect. One more realistic requirement for the same photographer site: Add client-side CSV backup/restore for the gallery metadata (fields: id, title, category, caption) plus drag-and-drop reordering. Specifically: An \"Export CSV\" button that downloads gallery.csv and an \"Import CSV\" file input that restores the gallery from a CSV. The CSV must correctly handle captions containing commas, double-quotes, and line breaks per RFC 4180 (quoted fields, doubled quotes), include a UTF-8 BOM so Excel opens it correctly, and be lossless on round-trip (Export -> Import should restore identical data). Also make the gallery cards draggable to reorder, and persist the order in localStorage so it survives page reload. Keep it vanilla JS with no external libraries.",
]

def call_openrouter(messages):
    payload = {
        "model": MODEL,
        "messages": messages,
        "reasoning": {"effort": "medium"},
        "temperature": 0.7,
        "max_tokens": 8192,
    }
    resp = requests.post(API_URL, headers=headers, json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    content = data["choices"][0]["message"]["content"]
    return content, data

def main():
    messages = []
    full_log = {
        "model": MODEL,
        "generation_settings": {"reasoning": {"effort": "medium"}, "temperature": 0.7, "max_tokens": 8192},
        "messages": [],
        "raw_responses": [],
    }
    for i, turn in enumerate(TURNS, 1):
        print(f"\n=== Turn {i} USER ===\n{turn[:120]}...")
        messages.append({"role": "user", "content": turn})
        print(f"Calling {MODEL} (medium reasoning)...")
        content, raw = call_openrouter(messages)
        print(f"=== Turn {i} ASSISTANT ({len(content)} chars) ===")
        print(content[:500])
        messages.append({"role": "assistant", "content": content})
        full_log["messages"] = messages.copy()
        full_log["raw_responses"].append(raw)
        # naive extract: save code blocks to website/ after last turn manually — do not auto-repair
        time.sleep(1)

    out = Path("conversation/conversation.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(full_log, indent=2))
    print(f"\nSaved {out}")

if __name__ == "__main__":
    main()
