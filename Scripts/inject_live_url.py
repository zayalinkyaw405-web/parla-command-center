"""
Scripts/inject_live_url.py
===========================
Injects the active public Cloudflare URL into all pitch packages and outbound files.
"""

import json
from pathlib import Path

LIVE_URL = "https://fog-coastal-talk-duck.trycloudflare.com"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTBOUND_DIR = PROJECT_ROOT / "Project" / "outbound_prospects"

def update_file(path: Path):
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    if "[INSERT YOUR TRYCLOUDFLARE URL HERE]" in text or "http://127.0.0.1:8000" in text:
        new_text = text.replace("[INSERT YOUR TRYCLOUDFLARE URL HERE]", LIVE_URL)
        new_text = new_text.replace("http://127.0.0.1:8000", LIVE_URL)
        path.write_text(new_text, encoding="utf-8")
        print(f" [+] Updated Live URL in: {path.relative_to(PROJECT_ROOT)}")

def main():
    print("=" * 80)
    print(f"      INJECTING LIVE PUBLIC URL ({LIVE_URL})")
    print("=" * 80)
    for p in OUTBOUND_DIR.rglob("*.*"):
        if p.suffix in [".txt", ".md", ".json"]:
            update_file(p)
    print("=" * 80)
    print(" [PASS] All outbound pitch materials updated with live URL.")

if __name__ == "__main__":
    main()
