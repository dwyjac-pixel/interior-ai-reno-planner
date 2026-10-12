#!/usr/bin/env python3
"""Render privacy.md + index content into the static site pages.

Usage: build_site.py <policy.md> <out_dir>
Minimal Markdown: #/##/### headings, paragraphs, - bullets, **bold**, [text](url), `code`.
"""
import html
import re
import sys
from pathlib import Path

EFFECTIVE = "September 11, 2026"
APP = "Interior AI Reno Planner"
COMPANY = "Caribinal Creations Ltd."
CONTACT = "info@caribinalcreations.com"
SITE = "https://caribinalcreations.ca"
APP_STORE = "https://apps.apple.com/ca/app/id6804528486"


def inline(text: str) -> str:
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    text = re.sub(r"\[(.+?)\]\((https?://[^)\s]+|mailto:[^)\s]+)\)", r'<a href="\2">\1</a>', text)
    text = re.sub(r"(?<![\"'>=])(https?://[^\s<)]*[^\s<).,;:!?])", r'<a href="\1">\1</a>', text)
    text = re.sub(r"(?<![\w/@\"'>])([\w.+-]+@[\w-]+(?:\.[\w-]+)*\.[A-Za-z]{2,})", r'<a href="mailto:\1">\1</a>', text)
    return text


def md_to_html(md: str) -> str:
    out, para, lst = [], [], None

    def flush_para():
        nonlocal para
        if para:
            out.append(f"<p>{inline(' '.join(para))}</p>")
            para = []

    def flush_list():
        nonlocal lst
        if lst:
            out.append("<ul>" + "".join(f"<li>{inline(i)}</li>" for i in lst) + "</ul>")
            lst = None

    for raw in md.splitlines():
        line = raw.rstrip()
        if not line.strip():
            flush_para(); flush_list(); continue
        m = re.match(r"^(#{1,3})\s+(.*)$", line)
        if m:
            flush_para(); flush_list()
            level = len(m.group(1))
            title = m.group(2).strip()
            if level == 1:
                continue  # page template supplies the H1
            slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
            out.append(f'<h{level} id="{slug}">{inline(title)}</h{level}>')
            continue
        m = re.match(r"^\s*[-*]\s+(.*)$", line)
        if m:
            flush_para()
            lst = (lst or []) + [m.group(1).strip()]
            continue
        flush_list()
        para.append(line.strip())
    flush_para(); flush_list()
    return "\n".join(out)


STYLE = """
:root{--bg:#f7f6f4;--card:#ffffff;--ink:#1c1c1e;--muted:#6b6b70;--accent:#d63a4a;--rule:#e6e3df;--code:#f0eeea}
@media (prefers-color-scheme:dark){:root{--bg:#141416;--card:#1e1e21;--ink:#f2f2f4;--muted:#a0a0a8;--accent:#ff6b7a;--rule:#2e2e33;--code:#26262b}}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
header{border-bottom:1px solid var(--rule);background:var(--card)}
.wrap{max-width:760px;margin:0 auto;padding:0 20px}
.brand{display:flex;align-items:center;gap:12px;padding:18px 0;text-decoration:none;color:var(--ink)}
.brand .mark{width:40px;height:40px;border-radius:10px;background:linear-gradient(145deg,#e8455a,#b8202f);display:grid;place-items:center;color:#fff;font-weight:700;font-size:18px;flex:none}
.brand .name{font-weight:600;font-size:16px}.brand .co{color:var(--muted);font-size:13px;display:block}
main{padding:28px 0 56px}
h1{font-size:34px;line-height:1.15;margin:0 0 6px;letter-spacing:-.01em}
.meta{color:var(--muted);margin:0 0 28px;font-size:15px}
h2{font-size:22px;margin:36px 0 10px;padding-top:8px;letter-spacing:-.01em}
h3{font-size:18px;margin:24px 0 6px}
p{margin:0 0 14px}ul{margin:0 0 16px;padding-left:22px}li{margin:4px 0}
a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}
code{background:var(--code);padding:2px 6px;border-radius:6px;font-size:.9em}
.summary{background:var(--card);border:1px solid var(--rule);border-radius:14px;padding:18px 20px;margin:0 0 8px}
.summary h2{margin:0 0 8px;font-size:18px;padding:0}
.summary ul{margin:0}
footer{border-top:1px solid var(--rule);color:var(--muted);font-size:14px;padding:22px 0}
footer nav a{margin-right:16px}
.card{background:var(--card);border:1px solid var(--rule);border-radius:14px;padding:22px 24px;margin:18px 0}
.hero{padding:40px 0 10px}.hero p{font-size:19px;color:var(--muted)}
.btn{display:inline-block;background:var(--accent);color:#fff!important;padding:10px 16px;border-radius:10px;font-weight:600}
.store{display:inline-flex;align-items:center;gap:10px;background:#000;color:#fff!important;padding:11px 20px;border-radius:12px;font-weight:600;font-size:17px;border:1px solid rgba(255,255,255,.25);text-decoration:none!important}
.store svg{width:20px;height:20px;fill:#fff;flex:none}
.store small{display:block;font-weight:400;font-size:12px;line-height:1.1;opacity:.85}
@media (max-width:480px){body{font-size:16px}h1{font-size:28px}h2{font-size:20px}}
"""


def page(title: str, body: str, description: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en-CA">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{html.escape(description, quote=True)}">
<meta name="color-scheme" content="light dark">
<title>{html.escape(title)}</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%23d63a4a'/%3E%3Cpath d='M14 34 32 18l18 16v18H14z' fill='none' stroke='%23fff' stroke-width='4' stroke-linejoin='round'/%3E%3C/svg%3E">
<style>{STYLE}</style>
</head>
<body>
<header><div class="wrap"><a class="brand" href="./"><span class="mark">IR</span><span><span class="name">{APP}</span><span class="co">by {COMPANY}</span></span></a></div></header>
<main><div class="wrap">
{body}
</div></main>
<footer><div class="wrap"><nav><a href="./">Home</a><a href="./privacy.html">Privacy Policy</a><a href="{SITE}">{SITE.replace('https://', '')}</a><a href="mailto:{CONTACT}">{CONTACT}</a></nav>
<p>&copy; 2026 {COMPANY} &middot; Winnipeg, Manitoba, Canada</p></div></footer>
</body>
</html>
"""


def main() -> None:
    policy_md = Path(sys.argv[1]).read_text(encoding="utf-8")
    out = Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)

    body_html = md_to_html(policy_md)
    # Wrap the Summary section (first h2 + its list) in a highlighted card.
    body_html = re.sub(
        r'(<h2 id="summary">Summary</h2>\s*<ul>.*?</ul>)',
        r'<div class="summary">\1</div>',
        body_html, count=1, flags=re.S,
    )
    privacy_body = (
        f"<h1>Privacy Policy</h1>\n"
        f'<p class="meta">{APP} for iPhone and iPad &middot; Effective {EFFECTIVE}</p>\n'
        f"{body_html}"
    )
    (out / "privacy.html").write_text(
        page(f"Privacy Policy — {APP}", privacy_body,
             f"How {APP} by {COMPANY} handles your data: on-device storage, iCloud sync in your own account, optional AI features, and no tracking."),
        encoding="utf-8")

    index_body = f"""<div class="hero">
<h1>{APP}</h1>
<p>Scan a basement with your iPhone or iPad, get a measured floor plan and 3D model, run the legal-suite compliance check, price the material takeoff, and hand the client a finished report — all from one app built by a Manitoba basement contractor.</p>
<p style="margin:6px 0 0"><a class="store" href="{APP_STORE}"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M16.37 12.6c0-2.5 2.05-3.7 2.14-3.76-1.17-1.7-2.98-1.94-3.62-1.97-1.54-.16-3.01.9-3.79.9-.78 0-1.99-.88-3.27-.86-1.68.03-3.23.98-4.1 2.48-1.75 3.03-.45 7.52 1.26 9.98.83 1.2 1.82 2.55 3.12 2.5 1.25-.05 1.73-.81 3.24-.81 1.51 0 1.94.81 3.27.79 1.35-.03 2.2-1.22 3.03-2.43.95-1.4 1.34-2.75 1.36-2.82-.03-.01-2.62-1-2.64-4zM13.9 5.25c.69-.84 1.16-2 1.03-3.16-1 .04-2.2.66-2.92 1.5-.64.74-1.2 1.93-1.05 3.07 1.11.09 2.25-.57 2.94-1.41z"/></svg><span><small>Download on the</small>App Store</span></a></p>
<p style="margin:10px 0 0;color:var(--muted);font-size:15px">Free for iPhone and iPad. LiDAR scanning needs an iPhone 12 Pro or later or an iPad Pro; every other feature works on any device.</p>
</div>
<div class="card">
<h2 style="margin-top:0">Support</h2>
<p>Questions, bug reports, or feature requests: email <a href="mailto:{CONTACT}">{CONTACT}</a> or visit <a href="{SITE}">{SITE.replace('https://', '')}</a>. We usually reply within two business days.</p>
</div>
<div class="card">
<h2 style="margin-top:0">Privacy</h2>
<p>Your projects stay on your device and in your own iCloud account. We run no servers, no analytics, and no ads.</p>
<p style="margin:0"><a class="btn" href="./privacy.html">Read the Privacy Policy</a></p>
</div>
"""
    (out / "index.html").write_text(
        page(f"{APP} — Support", index_body,
             f"Support and privacy information for {APP}, the basement and legal-suite renovation planner for iPhone and iPad by {COMPANY}."),
        encoding="utf-8")
    (out / ".nojekyll").write_text("", encoding="utf-8")
    print(f"wrote {out/'privacy.html'} and {out/'index.html'}")


if __name__ == "__main__":
    main()
