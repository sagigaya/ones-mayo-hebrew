"""
Fix broken image URLs: revert רטבים→salsas INSIDE URLs/paths only (not in text).
Patterns to fix: /wp-content/.../רטבים<rest>  →  /wp-content/.../salsas<rest>
                 רטבים10.png                   →  salsas10.png (standalone filename)
                 any רטבים-NNNxNNN.png         →  salsas-NNNxNNN.png
"""
import re
from pathlib import Path

ROOT = Path.home() / "Desktop" / "ones-mayo-hebrew"

HEB_TO_LATIN = [
    ("רטבים", "salsas"),
    ("מותגים", "MARCAS"),
    ("איכות", "CALIDAD"),
    ("חרדל", "mostaza"),
    ("מיונז", "mayonesa"),
]

def fix(path: Path):
    try: txt = path.read_text(encoding="utf-8")
    except: return False
    orig = txt

    # In-URL reversal: whenever a Hebrew word appears inside a URL path or filename
    # (i.e. between slashes, inside quotes, inside url() or next to - or . or digits),
    # revert it to its Latin original.
    for heb, lat in HEB_TO_LATIN:
        # Pattern: /...heb...  (anywhere after / inside URL-safe chars)
        txt = re.sub(
            r'(/[A-Za-z0-9._-]*)' + re.escape(heb) + r'([A-Za-z0-9._-]*)',
            lambda m: m.group(1) + lat + m.group(2),
            txt
        )
        # Keep running until no more matches (multiple heb words in same URL)
        prev = None
        while prev != txt:
            prev = txt
            txt = re.sub(
                r'(/[A-Za-z0-9._-]*)' + re.escape(heb) + r'([A-Za-z0-9._-]*)',
                lambda m: m.group(1) + lat + m.group(2),
                txt
            )
        # Also: filename with leading quote/paren/= and immediate heb+digit or heb-digit or heb.png
        txt = re.sub(
            r'(["\'=(,\s])([A-Za-z0-9._-]*)' + re.escape(heb) + r'([A-Za-z0-9._-]*\.(?:png|jpg|jpeg|gif|webp|svg|pdf|ico))',
            lambda m: m.group(1) + m.group(2) + lat + m.group(3),
            txt, flags=re.IGNORECASE
        )

    if txt != orig:
        path.write_text(txt, encoding="utf-8")
        return True
    return False

def main():
    htmls = sorted(ROOT.rglob("*.html"))
    print(f"Fixing broken URLs in {len(htmls)} files...")
    n = 0
    for p in htmls:
        rel = str(p.relative_to(ROOT))
        if any(s in rel for s in ("wp-json","feed","oembed","comments")): continue
        if fix(p): n += 1

    # Also check CSS files
    csss = sorted(ROOT.rglob("*.css"))
    for p in csss:
        if fix(p): n += 1
    print(f"✓ {n} files fixed.")

    # Verify
    bad = 0
    for p in htmls + csss:
        if 'wp-json' in str(p) or 'feed' in str(p): continue
        try:
            t = p.read_text(encoding='utf-8')
            if re.search(r'(?:/|["\'])(רטבים\d)', t):
                bad += 1
                if bad <= 3: print(f"  STILL BAD: {p.relative_to(ROOT)}")
        except: pass
    print(f"\n→ Files still containing bad URLs: {bad}")

if __name__ == "__main__":
    main()
