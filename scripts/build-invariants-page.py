#!/usr/bin/env python3
"""Generate invariants.html — the full invariant and principle register — from FRAMEWORK.md.

FRAMEWORK.md is the source of truth. This script extracts the five invariant
categories (intro, entries, notes) and the principles section, cross-checks
them against the Reference tables, and emits a static page in the landing
page's design language.

Usage:
    python3 scripts/build-invariants-page.py            # write invariants.html
    python3 scripts/build-invariants-page.py --check    # exit 1 if invariants.html is stale
"""

import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FRAMEWORK = ROOT / "FRAMEWORK.md"
OUTPUT = ROOT / "invariants.html"
REPO_BLOB = "https://github.com/geoffbelknap/ask/blob/main/"


def md_inline(text):
    """Convert the markdown subset used in FRAMEWORK.md bodies to HTML."""
    text = html.escape(text, quote=False)
    # links: relative .md targets go to the GitHub-rendered file
    def link(m):
        label, target = m.group(1), m.group(2)
        if not target.startswith(("http://", "https://")):
            target = REPO_BLOB + target
        return f'<a href="{target}">{label}</a>'
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    return text


def md_block(para):
    """Render one body paragraph, expanding markdown list lines into a <ul>."""
    lines = para.splitlines()
    if not any(line.startswith("- ") for line in lines):
        return f"<p>{md_inline(para)}</p>"
    out, lead = [], []
    for line in lines:
        if line.startswith("- "):
            out.append(f"<li>{md_inline(line[2:].strip())}</li>")
        else:
            lead.append(line)
    lead_html = f"<p>{md_inline(' '.join(lead))}</p>" if lead else ""
    return f'{lead_html}<ul class="invariant-list-items">{"".join(out)}</ul>'


def parse_framework(src):
    version_m = re.search(r"\*\*Version: (ASK \d{4}\.\d{2})\*\*", src)
    if not version_m:
        sys.exit("build-invariants-page: no version line in FRAMEWORK.md")
    version = version_m.group(1)

    inv_section = src.split("## The Invariants", 1)[1].split("## The Principles", 1)[0]
    categories = []
    for block in re.split(r"^### ", inv_section, flags=re.M)[1:]:
        lines = block.splitlines()
        title = lines[0].strip()
        body = "\n".join(lines[1:])
        first_inv = body.find("**INV-")
        intro = " ".join(p.strip() for p in body[:first_inv].strip().splitlines() if p.strip())
        entries = []
        for m in re.finditer(
            r"\*\*INV-(\d{2}) — (.*?)\.\*\* `([a-z0-9-]+)`\n(.*?)(?=\n\*\*INV-|\Z)",
            body,
            re.S,
        ):
            num, statement, slug, rest = m.groups()
            paras = []
            for raw in rest.strip().split("\n\n"):
                raw = raw.strip()
                if not raw or raw == "---":
                    continue
                if any(line.startswith("- ") for line in raw.splitlines()):
                    paras.append(raw)  # keep list paragraphs line-structured
                else:
                    paras.append(raw.replace("\n", " "))
            body_paras = [p for p in paras if not (p.startswith("*") and p.endswith("*") and not p.startswith("**"))]
            notes = [p[1:-1] for p in paras if p.startswith("*") and p.endswith("*") and not p.startswith("**")]
            entries.append({
                "num": num, "statement": statement, "slug": slug,
                "body": body_paras, "notes": notes,
            })
        categories.append({"title": title, "intro": intro, "entries": entries})

    prin_section = src.split("## The Principles", 1)[1]
    prin_section = re.split(r"^## ", prin_section, flags=re.M)[0]
    prin_intro_src = prin_section.split("| # |", 1)[0]
    prin_intro = [
        p.strip().replace("\n", " ")
        for p in prin_intro_src.strip().split("\n\n")
        if p.strip() and not p.strip().startswith("**")
    ][:2]
    principles = []
    for m in re.finditer(r"^\| PRIN-(\d{2}) \| (.*?) \| `([a-z0-9-]+)` \|", prin_section, re.M):
        num, statement, slug = m.groups()
        statement = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", statement)
        principles.append({"num": num, "statement": statement, "slug": slug, "note": None})
    for m in re.finditer(r"\*\*On `([a-z0-9-]+)` \(PRIN-\d{2}\)\.\*\* (.*?)(?=\n\n|\Z)", prin_section, re.S):
        slug, note = m.group(1), m.group(2).strip().replace("\n", " ")
        for p in principles:
            if p["slug"] == slug:
                p["note"] = note

    # Cross-check against the Reference tables.
    ref_inv = re.findall(r"^\| INV-\d{2} \| `([a-z0-9-]+)` \|", src, re.M)
    got_inv = [e["slug"] for c in categories for e in c["entries"]]
    if sorted(ref_inv) != sorted(got_inv) or len(got_inv) != 38:
        sys.exit(
            f"build-invariants-page: invariant mismatch — parsed {len(got_inv)}, "
            f"reference table has {len(ref_inv)}; diff: "
            f"{sorted(set(ref_inv) ^ set(got_inv))}"
        )
    if len(principles) != 14:
        sys.exit(f"build-invariants-page: expected 14 principles, parsed {len(principles)}")

    return version, categories, principles, prin_intro


PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>ASK — The Invariants and Principles</title>
<meta name="description" content="The full register of ASK's {inv_count} invariants and {prin_count} principles. Every invariant is binary, externally verifiable, and carries a verification test."/>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,300;9..144,400&family=DM+Sans:wght@300;400;500&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet"/>
<style>
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
:root {{
  --warm: #FDFAF5;
  --ink: #1A1714;
  --ink-mid: #6B6560;
  --ink-faint: #B8B2AC;
  --teal: #00A882;
  --teal-dark: #007A62;
  --teal-light: #E1F5EE;
  --teal-border: #B8E8D8;
  --border: #E8E2D9;
  --border-mid: #D4CEC8;
  --serif: 'Fraunces', serif;
  --sans: 'DM Sans', sans-serif;
  --mono: 'Space Mono', monospace;
  --nav-h: 56px;
}}
html {{ scroll-behavior: smooth; }}
body {{
  background: var(--warm);
  color: var(--ink);
  font-family: var(--sans);
  font-size: 16px;
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
}}
nav {{
  position: sticky; top: 0; z-index: 200;
  background: rgba(253,250,245,0.94);
  backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px);
  border-bottom: 0.5px solid var(--border);
  padding: 0 40px; height: var(--nav-h);
  display: flex; align-items: center; justify-content: space-between;
}}
.nav-brand {{ display: flex; align-items: center; gap: 12px; text-decoration: none; }}
.nav-wordmark {{ font-family: var(--mono); font-size: 14px; font-weight: 700; color: var(--ink); letter-spacing: 0.05em; }}
.nav-sub {{ font-family: var(--mono); font-size: 11px; color: var(--ink-faint); }}
.nav-links {{ display: flex; align-items: center; gap: 28px; list-style: none; }}
.nav-links a {{ font-size: 14px; color: var(--ink-mid); text-decoration: none; transition: color 0.15s; }}
.nav-links a:hover {{ color: var(--ink); }}
header.register {{ max-width: 960px; margin: 0 auto; padding: 64px 40px 8px; }}
.register-version {{ font-family: var(--mono); font-size: 11px; color: var(--teal-dark); letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 14px; }}
header.register h1 {{ font-family: var(--serif); font-weight: 400; font-size: clamp(28px, 4vw, 40px); line-height: 1.15; letter-spacing: -0.02em; max-width: 640px; margin-bottom: 14px; }}
.register-sub {{ font-size: 15px; color: var(--ink-mid); max-width: 620px; line-height: 1.7; }}
.register-toc {{ max-width: 960px; margin: 0 auto; padding: 24px 40px 0; display: flex; flex-wrap: wrap; gap: 10px; }}
.register-toc a {{ font-family: var(--mono); font-size: 11px; color: var(--ink-mid); text-decoration: none; border: 0.5px solid var(--border-mid); border-radius: 999px; padding: 6px 14px; transition: color 0.15s, border-color 0.15s; }}
.register-toc a:hover {{ color: var(--ink); border-color: var(--ink-mid); }}
section {{ max-width: 960px; margin: 0 auto; padding: 40px 40px; }}
.section-label {{ font-family: var(--mono); font-size: 11px; color: var(--teal-dark); letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 12px; }}
.section-heading {{ font-family: var(--serif); font-weight: 400; font-size: clamp(22px, 3vw, 28px); line-height: 1.2; letter-spacing: -0.02em; max-width: 640px; margin-bottom: 10px; }}
.section-sub {{ font-size: 15px; color: var(--ink-mid); max-width: 620px; line-height: 1.7; margin-bottom: 28px; }}
.section-divider {{ border: none; border-top: 0.5px solid var(--border); }}
.invariants-list {{ display: flex; flex-direction: column; gap: 1px; background: var(--border); border: 0.5px solid var(--border); border-radius: 10px; overflow: hidden; }}
.invariant {{ background: var(--warm); padding: 18px 20px; display: flex; gap: 16px; scroll-margin-top: calc(var(--nav-h) + 16px); }}
.invariant:target {{ background: var(--teal-light); }}
.invariant-num {{ flex-shrink: 0; width: 46px; padding-top: 3px; }}
.invariant-num a {{ font-family: var(--mono); font-size: 10px; color: var(--teal-dark); text-decoration: none; }}
.invariant-num a:hover {{ text-decoration: underline; }}
.invariant-body {{ font-size: 13.5px; line-height: 1.65; }}
.invariant-body strong {{ font-weight: 500; color: var(--ink); }}
.invariant-body p {{ color: var(--ink-mid); margin-top: 4px; }}
.invariant-body p.note {{ font-style: italic; color: var(--ink-faint); }}
.invariant-body p.note em {{ font-style: normal; }}
.invariant-body a {{ color: var(--teal-dark); }}
.invariant-body code {{ font-family: var(--mono); font-size: 11.5px; }}
.invariant-list-items {{ color: var(--ink-mid); margin: 4px 0 4px 20px; }}
.invariant-list-items li {{ margin-bottom: 2px; }}
.invariant-slug {{ font-family: var(--mono); font-size: 11px; color: var(--ink-faint); margin-left: 8px; white-space: nowrap; }}
footer {{ border-top: 0.5px solid var(--border); padding: 28px 40px; margin-top: 32px; }}
.footer-inner {{ max-width: 960px; margin: 0 auto; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px; }}
.footer-brand {{ font-family: var(--mono); font-size: 13px; font-weight: 700; color: var(--ink); text-decoration: none; }}
.footer-links {{ display: flex; gap: 24px; list-style: none; flex-wrap: wrap; }}
.footer-links a {{ font-size: 13px; color: var(--ink-mid); text-decoration: none; }}
.footer-links a:hover {{ color: var(--ink); }}
.footer-copy {{ font-size: 11px; color: var(--ink-faint); font-family: var(--mono); }}
@media (max-width: 720px) {{
  nav {{ padding: 0 20px; }}
  .nav-links {{ gap: 16px; }}
  header.register, .register-toc, section {{ padding-left: 20px; padding-right: 20px; }}
  .invariant {{ flex-direction: column; gap: 6px; }}
}}
</style>
</head>
<body>

<nav>
  <a href="index.html" class="nav-brand">
    <span class="nav-wordmark">ASK</span>
    <span class="nav-sub">Agent Security</span>
  </a>
  <ul class="nav-links">
    <li><a href="index.html">Overview</a></li>
    <li><a href="#invariants">Invariants</a></li>
    <li><a href="#principles">Principles</a></li>
    <li><a href="https://github.com/geoffbelknap/ask">GitHub</a></li>
  </ul>
</nav>

<header class="register">
  <div class="register-version">{version} — full register</div>
  <h1>The invariants and principles, in full.</h1>
  <p class="register-sub">Every property the framework requires, on one page. An invariant is binary — at any moment it holds or it is violated — and externally verifiable: every one carries a test in <a href="{blob}VERIFICATION.md" style="color:var(--teal-dark);">VERIFICATION.md</a>. A principle is the judgment the framework names rather than pretends to automate. Each entry has a stable link: cite it by its number or slug.</p>
</header>

<div class="register-toc">
{toc}
</div>

{sections}

<hr class="section-divider"/>

<section id="principles">
  <div class="section-label">The principles</div>
  <h2 class="section-heading">{prin_count} judgment calls, named.</h2>
  {prin_intro}
  <div class="invariants-list">
{principles}
  </div>
</section>

<footer>
  <div class="footer-inner">
    <a href="index.html" class="footer-brand">ASK</a>
    <ul class="footer-links">
      <li><a href="index.html">Overview</a></li>
      <li><a href="https://github.com/geoffbelknap/ask">GitHub</a></li>
      <li><a href="{blob}FRAMEWORK.md">Framework</a></li>
      <li><a href="{blob}VERIFICATION.md">Verification</a></li>
    </ul>
    <span class="footer-copy">{version} — CC BY 4.0 — generated from FRAMEWORK.md</span>
  </div>
</footer>

</body>
</html>
"""


def render(version, categories, principles, prin_intro_paras):
    toc_items, sections = [], []
    for i, cat in enumerate(categories):
        cat_id = re.sub(r"[^a-z0-9]+", "-", cat["title"].lower()).strip("-")
        toc_items.append(f'  <a href="#{cat_id}">{html.escape(cat["title"])}</a>')
        entries = []
        for e in cat["entries"]:
            paras = "".join(md_block(p) for p in e["body"])
            notes = "".join(f'<p class="note">{md_inline(p)}</p>' for p in e["notes"])
            entries.append(
                f'      <div class="invariant" id="inv-{e["num"]}">'
                f'<div class="invariant-num"><a href="#inv-{e["num"]}">INV-{e["num"]}</a></div>'
                f'<div class="invariant-body" id="{e["slug"]}">'
                f'<strong>{md_inline(e["statement"])}.</strong>'
                f'<span class="invariant-slug">{e["slug"]}</span>'
                f"{paras}{notes}</div></div>"
            )
        divider = '<span id="invariants"></span>\n' if i == 0 else '<hr class="section-divider"/>\n\n'
        sections.append(
            f'{divider}<section id="{cat_id}">\n'
            f'  <div class="section-label">Invariants — category {i + 1} of {len(categories)}</div>\n'
            f'  <h2 class="section-heading">{html.escape(cat["title"])}.</h2>\n'
            f'  <p class="section-sub">{md_inline(cat["intro"])}</p>\n'
            f'  <div class="invariants-list">\n'
        )
        sections.append("\n".join(entries) + "\n  </div>\n</section>\n")
    toc_items.append('  <a href="#principles">The principles</a>')

    prin_rows = []
    for p in principles:
        note = f'<p class="note">{md_inline(p["note"])}</p>' if p["note"] else ""
        prin_rows.append(
            f'      <div class="invariant" id="prin-{p["num"]}">'
            f'<div class="invariant-num"><a href="#prin-{p["num"]}">PRIN-{p["num"]}</a></div>'
            f'<div class="invariant-body" id="{p["slug"]}">'
            f'<strong>{md_inline(p["statement"])}.</strong>'
            f'<span class="invariant-slug">{p["slug"]}</span>{note}</div></div>'
        )
    prin_intro = "".join(
        f'<p class="section-sub" style="margin-bottom:14px;">{md_inline(p)}</p>'
        for p in prin_intro_paras
    )

    inv_count = sum(len(c["entries"]) for c in categories)
    return PAGE.format(
        version=version,
        blob=REPO_BLOB,
        inv_count=inv_count,
        prin_count=len(principles),
        toc="\n".join(toc_items),
        sections="\n".join(sections),
        prin_intro=prin_intro,
        principles="\n".join(prin_rows),
    )


def main():
    version, categories, principles, prin_intro = parse_framework(FRAMEWORK.read_text())
    page = render(version, categories, principles, prin_intro)
    if "--check" in sys.argv:
        if not OUTPUT.exists() or OUTPUT.read_text() != page:
            sys.exit("build-invariants-page: invariants.html is stale — rerun scripts/build-invariants-page.py")
        print("build-invariants-page: invariants.html is current")
        return
    OUTPUT.write_text(page)
    print(f"build-invariants-page: wrote {OUTPUT.name} ({version}, {sum(len(c['entries']) for c in categories)} invariants, {len(principles)} principles)")


if __name__ == "__main__":
    main()
