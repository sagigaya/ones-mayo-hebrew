"""
Mirror onesmay.com — fetch all HTML pages + their dependent CSS/JS/images/fonts.
Saves everything under ~/Desktop/ones-mayo-hebrew/ preserving URL paths.
"""
import os, re, sys, urllib.parse, urllib.request, ssl, concurrent.futures
from pathlib import Path

ROOT = Path.home() / "Desktop" / "ones-mayo-hebrew"
BASE = "https://onesmay.com"
ORIGIN = urllib.parse.urlparse(BASE).netloc
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
HDR = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15"}

PAGES = [
    "/", "/empresa/",
    "/productos/mayonesa/", "/productos/base-tomate/", "/productos/mostazas/", "/productos/otras-salsas/",
    "/canales/", "/canales/horeca/", "/canales/retail/", "/canales/marca-privada/", "/canales/proyecto-industrial/",
    "/recetas/", "/noticias/", "/contacto/",
    "/aviso-legal/", "/politica-de-privacidad/", "/politica-de-cookies/",
]

visited = set()
assets_queued = set()
lock_count = [0]

def url_to_path(url):
    p = urllib.parse.urlparse(url)
    path = p.path
    if path.endswith("/") or path == "":
        path = (path or "/") + "index.html"
    if p.query:
        # append query hash to filename to avoid cache busting breaking paths
        base, ext = os.path.splitext(path)
        qh = str(abs(hash(p.query)))[:8]
        path = f"{base}--{qh}{ext}"
    return ROOT / path.lstrip("/")

def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers=HDR)
    with urllib.request.urlopen(req, context=CTX, timeout=timeout) as r:
        return r.read()

def save(target: Path, data: bytes):
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "wb") as f:
        f.write(data)

def rewrite_html_urls(html_bytes: bytes) -> tuple[bytes, list[str]]:
    """Return (modified bytes, list of absolute asset URLs to also fetch)."""
    txt = html_bytes.decode("utf-8", errors="replace")
    assets = set()

    def collect(m, attr_q, url):
        full = urllib.parse.urljoin(BASE + "/", url)
        p = urllib.parse.urlparse(full)
        if p.netloc and p.netloc != ORIGIN:
            return m.group(0)  # keep external URLs as-is
        # queue for fetch
        assets.add(full)
        # rewrite to local relative path
        local = url_to_path(full).relative_to(ROOT)
        # make root-absolute so it works from any sub-path
        return m.group(0).replace(url, "/" + str(local))

    # src="…" / href="…" / srcset="… ,…" / url(…)
    for pat in [
        r'(src)=(")([^"]+)"',
        r"(src)=(')([^']+)'",
        r'(href)=(")([^"]+)"',
        r"(href)=(')([^']+)'",
        r'(poster)=(")([^"]+)"',
        r'(data-src)=(")([^"]+)"',
        r'(data-image)=(")([^"]+)"',
    ]:
        def repl(m):
            return collect(m, m.group(2), m.group(3))
        txt = re.sub(pat, repl, txt)

    # srcset — comma-separated URLs
    def srcset_repl(m):
        full_attr = m.group(0)
        new_parts = []
        for part in m.group(2).split(","):
            part = part.strip()
            if not part:
                continue
            sp = part.rsplit(" ", 1)
            u = sp[0]
            if urllib.parse.urlparse(urllib.parse.urljoin(BASE + "/", u)).netloc == ORIGIN:
                full = urllib.parse.urljoin(BASE + "/", u)
                assets.add(full)
                u = "/" + str(url_to_path(full).relative_to(ROOT))
            new_parts.append(u if len(sp) == 1 else u + " " + sp[1])
        new_val = ", ".join(new_parts)
        return f'{m.group(1)}="{new_val}"'
    txt = re.sub(r'(srcset)="([^"]+)"', srcset_repl, txt)

    # url(…) in inline styles
    def css_url_repl(m):
        u = m.group(1).strip().strip("'\"")
        full = urllib.parse.urljoin(BASE + "/", u)
        if urllib.parse.urlparse(full).netloc != ORIGIN:
            return m.group(0)
        assets.add(full)
        local = "/" + str(url_to_path(full).relative_to(ROOT))
        return f"url({local})"
    txt = re.sub(r"url\(([^)]+)\)", css_url_repl, txt)

    return txt.encode("utf-8"), list(assets)

def process_css(css_bytes: bytes, css_url: str) -> tuple[bytes, list[str]]:
    """Rewrite url(...) inside CSS, collecting assets."""
    txt = css_bytes.decode("utf-8", errors="replace")
    assets = set()
    def repl(m):
        u = m.group(1).strip().strip("'\"")
        if u.startswith("data:"):
            return m.group(0)
        full = urllib.parse.urljoin(css_url, u)
        p = urllib.parse.urlparse(full)
        if p.netloc and p.netloc != ORIGIN:
            return m.group(0)
        assets.add(full)
        # relative path from the CSS file's directory
        css_local = url_to_path(css_url)
        asset_local = url_to_path(full)
        try:
            rel = os.path.relpath(asset_local, css_local.parent)
        except ValueError:
            rel = str(asset_local.relative_to(ROOT))
        return f"url({rel})"
    txt = re.sub(r"url\(([^)]+)\)", repl, txt)
    return txt.encode("utf-8"), list(assets)

def worker(url):
    if url in visited:
        return []
    visited.add(url)
    try:
        data = fetch(url)
    except Exception as e:
        print(f"  ✗ {url} :: {e}")
        return []
    target = url_to_path(url)
    ctype = ""
    # heuristic by extension
    ext = target.suffix.lower()
    new_assets = []
    if ext in {".html", ".htm", ""} or (b"<html" in data[:4096].lower()):
        if target.suffix == "":
            target = target / "index.html"
        new_data, new_assets = rewrite_html_urls(data)
        save(target, new_data)
    elif ext == ".css":
        new_data, new_assets = process_css(data, url)
        save(target, new_data)
    else:
        save(target, data)
    lock_count[0] += 1
    print(f"  ✓ [{lock_count[0]}] {url_to_path(url).relative_to(ROOT)}  ({len(data)//1024}KB)")
    return new_assets

def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    # Phase 1: fetch all main pages serially, collect assets
    all_assets = set()
    for p in PAGES:
        url = BASE + p
        new = worker(url)
        all_assets.update(new)
    print(f"\n→ Phase 1 done. {len(visited)} HTML pages. {len(all_assets)} assets queued.")

    # Phase 2: fetch assets in parallel; CSS may add more
    pending = list(all_assets - visited)
    seen = set(visited)
    while pending:
        print(f"\n→ Fetching {len(pending)} assets (parallel)...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
            futures = {ex.submit(worker, u): u for u in pending}
            new_pending = []
            for f in concurrent.futures.as_completed(futures):
                new_pending.extend(f.result() or [])
        seen |= visited
        pending = [u for u in set(new_pending) if u not in seen]

    print(f"\n✓ Mirror complete. {len(visited)} files total.")

if __name__ == "__main__":
    main()
