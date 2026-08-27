# Fraud-OSINT Wiki

A retro, low-bandwidth **MediaWiki-style static wiki** on **forensic accounting** and
**open-source intelligence (OSINT)** — the open handbook of how financial crime is detected,
investigated, proven in court, and traced across the open internet.

**Live site:** https://thumpersecure.github.io/fraud-osint/wiki/

## What this is

The wiki was built from a seven-document literature review (~1,142 pages of forensic-accounting
and OSINT training material) and then **verified and updated against live 2024–2026 research** —
the ACFE *Report to the Nations* (2024), the Nasdaq Verafin *Global Financial Crime Report* (2026),
FATF/FinCEN materials, and court/regulator records. It is organized as ~30 interlinked encyclopedic
articles that together read as a ~100-page report.

See **[About](https://thumpersecure.github.io/fraud-osint/wiki/About.html)** for sources and method,
and **[References](https://thumpersecure.github.io/fraud-osint/wiki/References.html)** for the full
bibliography.

## Design

Deliberately imitates the early-2000s MediaWiki "Monobook" skin: serif masthead, left nav column,
gold content rule, classic blue links. Every page is a few kilobytes of plain HTML sharing one
stylesheet — **no web fonts, no images, no analytics, no JavaScript required to read.** It loads
instantly on slow or metered connections, the way the early web did.

## Repository layout

```
skin/monobook.css        the single shared stylesheet (~5 KB)
articles/*.html          article source fragments (body + a <!--meta--> header line)
build.py                 wraps each fragment in the Monobook shell -> wiki/
wiki/*.html              the generated static site (what GitHub Pages serves)
research/                the briefs and harvested citations used to write the articles
```

## Building locally

```bash
python3 build.py          # regenerates everything in wiki/
```

Then open `wiki/index.html` in a browser. No dependencies beyond Python 3.

## Caveat

This is an **educational synthesis**, not legal, financial, or operational advice. Laws,
thresholds, and tools change; verify against the cited primary sources before relying on anything
here. Nothing in this repository should be used to target private individuals or to conduct
unauthorized access; see the *OSINT Ethics* article.
