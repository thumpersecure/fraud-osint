#!/usr/bin/env python3
"""Fraud-OSINT Wiki static-site builder.

Reads article fragments from articles/*.html (each an HTML body fragment with a
leading <!--meta title=... desc=... cats=...--> comment) and wraps them in the
retro Monobook shell. Zero runtime JS required; output is plain static HTML for
GitHub Pages. Deliberately minimal for low data use.
"""
import os
import re
import html
import glob

ROOT = os.path.dirname(os.path.abspath(__file__))
ART_DIR = os.path.join(ROOT, "articles")
OUT_DIR = os.path.join(ROOT, "wiki")

# Sidebar navigation — grouped like an old wiki's "portlets".
SIDEBAR = [
    ("navigation", [
        ("Main Page", "index.html"),
        ("About this wiki", "About.html"),
        ("Full report (one page)", "Full_Report.html"),
        ("Index of articles", "Index.html"),
        ("Glossary", "Glossary.html"),
        ("References", "References.html"),
    ]),
    ("forensic accounting", [
        ("Forensic Accounting", "Forensic_Accounting.html"),
        ("Fraud Triangle", "Fraud_Triangle.html"),
        ("Fraud Tree", "Fraud_Tree.html"),
        ("Occupational Fraud", "Occupational_Fraud.html"),
        ("Financial Statement Fraud", "Financial_Statement_Fraud.html"),
        ("Red Flags", "Red_Flags.html"),
        ("Analytical Methods", "Analytical_Methods.html"),
        ("Benford's Law", "Benfords_Law.html"),
        ("Net Worth Method", "Net_Worth_Method.html"),
        ("The ACFE Report to the Nations and Fraud Benchmark Surveys", "ACFE_Report_to_Nations.html"),
        ("Analytical Fraud-Detection Techniques: Benford's Law and Journal Entry Testing", "Fraud_Detection_Analytics.html"),
        ("The AML Statutory Framework: BSA, MLCA, FinCEN, and FATF", "AML_Statutory_Framework.html"),
        ("Anti-Bribery Law: The FCPA and UK Bribery Act", "Anti_Bribery_Statutes.html"),
        ("Professional Ethics Standards for Forensic Accountants", "Forensic_Accountant_Ethics.html"),
        ("U.S. Federal Financial Crime Enforcement Agencies", "Federal_Enforcement_Agencies.html"),
    ]),
    ("following the money", [
        ("Money Laundering", "Money_Laundering.html"),
        ("Asset Tracing", "Asset_Tracing.html"),
        ("Cryptocurrency Tracing", "Cryptocurrency_Tracing.html"),
        ("AML Law", "AML_Law.html"),
    ]),
    ("OSINT", [
        ("OSINT", "OSINT.html"),
        ("Intelligence Cycle", "Intelligence_Cycle.html"),
        ("OSINT Tools", "OSINT_Tools.html"),
        ("OSINT Disciplines", "OSINT_Disciplines.html"),
        ("OSINT Ethics", "OSINT_Ethics.html"),
    ]),
    ("investigation", [
        ("Digital Forensics", "Digital_Forensics.html"),
        ("Chain of Custody", "Chain_of_Custody.html"),
        ("Document Examination", "Document_Examination.html"),
        ("Interviewing", "Interviewing.html"),
        ("Evidence and Testimony", "Evidence_and_Testimony.html"),
        ("Report Writing", "Report_Writing.html"),
        ("Digital Forensics in Human Trafficking Financial Investigations", "Trafficking_Financial_Investigation.html"),
    ]),
    ("forensic science standards", [
        ("The Forensic Science Validity Crisis", "Forensic_Validity_Crisis.html"),
        ("Daubert, Frye, and Expert Testimony Admissibility", "Daubert_Standard.html"),
        ("The Brandon Mayfield Misidentification", "Brandon_Mayfield_Case.html"),
        ("The CSI Effect", "CSI_Effect.html"),
        ("The Scientific Working Groups (SWGDE, SWGDAM, SWGFAST, and More)", "SWG_Standards_Bodies.html"),
        ("NIST OSAC and the Modern Forensic Standards Ecosystem", "NIST_OSAC.html"),
        ("International Digital Forensics Standards: ISO, ENFSI, and INTERPOL", "International_Forensic_Standards.html"),
    ]),
    ("digital forensics", [
        ("The Digital Forensic Investigation Lifecycle", "Digital_Forensic_Lifecycle.html"),
        ("Data Standards for Cyber-Investigation: CASE, UCO, and WANDA", "Data_Standards_Cyber_Investigation.html"),
        ("Named Digital Forensics Tools: EnCase, Cellebrite, AXIOM, and Bulk Extractor", "Digital_Forensics_Tools.html"),
        ("Video and Multimedia Forensics: Tools and Certification", "Video_Forensics.html"),
        ("Machine Learning in Digital Forensics and the Explainability Problem", "ML_Forensics_Explainability.html"),
        ("Cloud, IoT, and Mobile Forensics Challenges", "Cloud_IoT_Forensics.html"),
    ]),
    ("forensic techniques", [
        ('Forensic Investigation Planning', "Forensic_Investigation_Planning.html"),
        ('Bank Statement and Cash Analysis', "Bank_Statement_and_Cash_Analysis.html"),
        ('Journal Entry and Ledger Testing', "Journal_Entry_and_Ledger_Testing.html"),
        ('Link and Network Analysis', "Link_and_Network_Analysis.html"),
        ('Revenue and Earnings Manipulation Tests', "Revenue_and_Earnings_Manipulation_Tests.html"),
        ('Forensic Interviewing and Statement Analysis', "Forensic_Interviewing_and_Statement_Analysis.html"),
        ('Business Valuation and Damages Quantification', "Business_Valuation_and_Damages_Quantification.html"),
        ('Litigation Support and Damages', "Litigation_Support_and_Damages.html"),
        ('Hidden Assets in Divorce and Bankruptcy', "Hidden_Assets_in_Divorce_and_Bankruptcy.html"),
    ]),
    ("fraud schemes", [
        ('Ponzi and Investment Fraud', "Ponzi_and_Investment_Fraud.html"),
        ('Procurement and Contract Fraud', "Procurement_and_Contract_Fraud.html"),
        ('Healthcare and Insurance Fraud', "Healthcare_and_Insurance_Fraud.html"),
        ('Payment Fraud and BEC', "Payment_Fraud_and_BEC.html"),
        ('Tax Fraud and Evasion', "Tax_Fraud_and_Evasion.html"),
        ('Public Sector Fraud and Improper Payments', "Public_Sector_Fraud_and_Improper_Payments.html"),
        ('Fraudster Psychology and the Dark Triad', "Fraudster_Psychology_and_Dark_Triad.html"),
        ('Financial Fraud Case Studies in Detection', "Financial_Fraud_Case_Studies_Detection.html"),
    ]),
    ("law and controls", [
        ('Internal Controls and Fraud Risk Assessment', "Internal_Controls_and_Fraud_Risk_Assessment.html"),
        ('Auditing Standards and Fraud', "Auditing_Standards_and_Fraud.html"),
        ('Whistleblowers and the False Claims Act', "Whistleblowers_and_the_False_Claims_Act.html"),
        ('Sanctions and Export Controls', "Sanctions_and_Export_Controls.html"),
        ('Shell Companies and Beneficial Ownership', "Shell_Companies_and_Beneficial_Ownership.html"),
    ]),
    ("OSINT methods", [
        ('Public Records and Court Dockets', "Public_Records_and_Court_Dockets.html"),
        ('Corporate Registries and Leak Databases', "Corporate_Registries_and_Leak_Databases.html"),
        ('Geolocation and Imagery OSINT', "Geolocation_and_Imagery_OSINT.html"),
        ('Web Archives and Domain Intelligence', "Web_Archives_and_Domain_Intelligence.html"),
    ]),
    ("applied", [
        ("Elder Financial Exploitation", "Elder_Financial_Exploitation.html"),
        ("Human Trafficking Finance", "Human_Trafficking_Finance.html"),
        ("Anti-Corruption OSINT", "Anti_Corruption_OSINT.html"),
        ("Case Studies", "Case_Studies.html"),
        ("Emerging Trends", "Emerging_Trends.html"),
        ("Occupational Stress and Burnout in Forensic Practice", "Forensic_Practitioner_Burnout.html"),
        ("AI and the Future of Fraud Detection Technology", "AI_Fraud_Detection_Platforms.html"),
    ]),
    ("case studies", [
        ("Major Financial Fraud Case Studies: Enron to Archegos", "Major_Fraud_Case_Studies.html"),
    ]),
]

SHELL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{desc}">
<title>{title} - Fraud-OSINT Wiki</title>
<link rel="stylesheet" href="{depth}skin/monobook.css">
</head>
<body>
<div id="globalWrapper">
<div id="siteTitle">
  <a href="{depth}wiki/index.html"><span class="logo">Fraud-OSINT Wiki</span></a>
  <span class="tagline">&mdash; the open handbook of forensic accounting &amp; open-source intelligence</span>
</div>
<div id="layout">
  <div id="column-one">
    <div class="portlet" id="p-logo"><a href="{depth}wiki/index.html">FRAUD&middot;OSINT</a></div>
    {sidebar}
    <div class="portlet">
      <h5>search</h5>
      <form id="searchform" onsubmit="return jump()">
        <input id="searchInput" type="text" placeholder="page name...">
        <div><input id="searchGo" type="submit" value="Go"></div>
      </form>
    </div>
  </div>
  <div id="content">
    <h1 id="firstHeading">{title}</h1>
    <div class="subtitle">From the Fraud-OSINT Wiki, the free forensic-accounting &amp; OSINT reference</div>
    {body}
    {catlinks}
  </div>
</div>
<div id="footer">
  <p>Fraud-OSINT Wiki &middot; built from a 7-source literature review &amp; live 2024&ndash;2026 research.
  Text is an educational synthesis; verify against primary sources before operational or legal use.</p>
  <p>Static site, no trackers, no cookies, no JavaScript required to read. Hosted on GitHub Pages.</p>
</div>
</div>
<script>
/* the ONLY script: a tiny client-side "Go" box. Page works fully without it. */
function jump(){{var v=document.getElementById('searchInput').value.trim();
if(!v)return false;var s=v.replace(/ /g,'_').replace(/[^A-Za-z0-9_'\\-]/g,'');
window.location.href=s+'.html';return false;}}
</script>
</body>
</html>
"""


def render_sidebar(active):
    out = []
    for heading, links in SIDEBAR:
        items = []
        for label, href in links:
            cls = ' class="active-page"' if href == active else ""
            items.append(f'<li{cls}><a href="{href}">{html.escape(label)}</a></li>')
        out.append(
            f'<div class="portlet"><h5>{html.escape(heading)}</h5>'
            f'<ul>{"".join(items)}</ul></div>'
        )
    return "\n    ".join(out)


def parse_meta(text):
    m = re.match(r"\s*<!--meta(.*?)-->", text, re.S)
    meta = {"title": "Untitled", "desc": "", "cats": ""}
    body = text
    if m:
        for k, v in re.findall(r'(\w+)="([^"]*)"', m.group(1)):
            meta[k] = v
        body = text[m.end():]
    return meta, body.strip()


# Order used for the single-page Full Report (matches the sidebar reading order).
REPORT_ORDER = [
    "Forensic_Accounting", "Fraud_Triangle", "Fraud_Tree", "Occupational_Fraud",
    "Financial_Statement_Fraud", "Red_Flags", "Analytical_Methods", "Benfords_Law",
    "Fraud_Detection_Analytics", "Net_Worth_Method",
    "ACFE_Report_to_Nations", "Forensic_Accountant_Ethics", "Federal_Enforcement_Agencies",
    "Anti_Bribery_Statutes", "AML_Statutory_Framework",
    "Money_Laundering", "Asset_Tracing", "Cryptocurrency_Tracing",
    "AML_Law", "OSINT", "Intelligence_Cycle", "OSINT_Tools", "OSINT_Disciplines",
    "OSINT_Ethics",
    "Forensic_Validity_Crisis", "Daubert_Standard", "Brandon_Mayfield_Case", "CSI_Effect",
    "SWG_Standards_Bodies", "NIST_OSAC", "International_Forensic_Standards",
    "Digital_Forensics", "Digital_Forensic_Lifecycle", "Data_Standards_Cyber_Investigation",
    "Digital_Forensics_Tools", "Video_Forensics", "ML_Forensics_Explainability",
    "Cloud_IoT_Forensics",
    "Chain_of_Custody", "Document_Examination",
    "Interviewing", "Evidence_and_Testimony", "Report_Writing",
    "Elder_Financial_Exploitation", "Human_Trafficking_Finance",
    "Trafficking_Financial_Investigation", "Anti_Corruption_OSINT",
    "Case_Studies", "Major_Fraud_Case_Studies",
    "Forensic_Investigation_Planning",
    "Bank_Statement_and_Cash_Analysis",
    "Journal_Entry_and_Ledger_Testing",
    "Link_and_Network_Analysis",
    "Revenue_and_Earnings_Manipulation_Tests",
    "Forensic_Interviewing_and_Statement_Analysis",
    "Business_Valuation_and_Damages_Quantification",
    "Litigation_Support_and_Damages",
    "Hidden_Assets_in_Divorce_and_Bankruptcy",
    "Ponzi_and_Investment_Fraud",
    "Procurement_and_Contract_Fraud",
    "Healthcare_and_Insurance_Fraud",
    "Payment_Fraud_and_BEC",
    "Tax_Fraud_and_Evasion",
    "Public_Sector_Fraud_and_Improper_Payments",
    "Fraudster_Psychology_and_Dark_Triad",
    "Financial_Fraud_Case_Studies_Detection",
    "Internal_Controls_and_Fraud_Risk_Assessment",
    "Auditing_Standards_and_Fraud",
    "Whistleblowers_and_the_False_Claims_Act",
    "Sanctions_and_Export_Controls",
    "Shell_Companies_and_Beneficial_Ownership",
    "Public_Records_and_Court_Dockets",
    "Corporate_Registries_and_Leak_Databases",
    "Geolocation_and_Imagery_OSINT",
    "Web_Archives_and_Domain_Intelligence",
    "Forensic_Practitioner_Burnout", "AI_Fraud_Detection_Platforms", "Emerging_Trends",
]

# Pages that are wiki-furniture, not part of the report narrative.
SKIP_FROM_REPORT = {"index", "Full_Report", "About", "Index", "Glossary", "References"}


def build():
    os.makedirs(OUT_DIR, exist_ok=True)
    files = sorted(glob.glob(os.path.join(ART_DIR, "*.html")))
    parsed = {}
    for path in files:
        with open(path, encoding="utf-8") as f:
            meta, body = parse_meta(f.read())
        base = os.path.basename(path)
        parsed[base[:-5]] = (base, meta, body)

    built = 0
    for stem, (base, meta, body) in parsed.items():
        cats = ""
        if meta.get("cats"):
            links = " | ".join(
                f'<a href="Category_{html.escape(c.strip().replace(" ", "_"))}.html">{html.escape(c.strip())}</a>'
                for c in meta["cats"].split(",") if c.strip()
            )
            cats = f'<div class="catlinks"><b>Categories:</b> {links}</div>'
        page = SHELL.format(
            title=html.escape(meta["title"]),
            desc=html.escape(meta.get("desc", "")),
            depth="../",
            sidebar=render_sidebar(base),
            body=body,
            catlinks=cats,
        )
        with open(os.path.join(OUT_DIR, base), "w", encoding="utf-8") as f:
            f.write(page)
        built += 1

    # ---- assemble the single-page Full Report ----
    parts = [
        '<p>This page collects every substantive article of the '
        '<a href="index.html">Fraud-OSINT Wiki</a> into one continuous document for printing or '
        'offline reading. Each section corresponds to a standalone article; internal links still '
        'work. For navigation, use the <a href="Index.html">Index</a>.</p>',
        '<div class="notebox">Generated automatically from the article sources. '
        'For sources see <a href="References.html">References</a>; for terms see '
        '<a href="Glossary.html">Glossary</a>.</div>',
        '<h2 id="report-toc">Contents</h2><ol>',
    ]
    for stem in REPORT_ORDER:
        if stem in parsed:
            t = parsed[stem][1]["title"]
            parts.append(f'<li><a href="#r-{stem}">{html.escape(t)}</a></li>')
    parts.append("</ol>")
    for stem in REPORT_ORDER:
        if stem not in parsed:
            continue
        base, meta, body = parsed[stem]
        # strip each article's own manual TOC and its trailing References list
        b = re.sub(r'<div class="toc">.*?</div>\s*</div>', "", body, flags=re.S)
        b = re.sub(r'<div class="toc">.*?</ul>\s*</div>', "", b, flags=re.S)
        parts.append(f'<h1 id="r-{stem}" style="border-bottom:2px solid #888;margin-top:1.4em;">'
                     f'{html.escape(meta["title"])}</h1>')
        parts.append(b)
        parts.append('<p class="hatnote">&mdash; end of section &mdash; '
                     '<a href="#report-toc">back to contents</a></p>')
    report_body = "\n".join(parts)
    report_page = SHELL.format(
        title="Full Report",
        desc="The complete Fraud-OSINT Wiki as one continuous, printable page.",
        depth="../",
        sidebar=render_sidebar("Full_Report.html"),
        body=report_body,
        catlinks='<div class="catlinks"><b>Categories:</b> <a href="Category_Wiki.html">Wiki</a></div>',
    )
    with open(os.path.join(OUT_DIR, "Full_Report.html"), "w", encoding="utf-8") as f:
        f.write(report_page)
    built += 1

    # ---- generate a real page for every category referenced ----
    cat_map = {}
    for stem, (base, meta, body) in parsed.items():
        for c in (meta.get("cats") or "").split(","):
            c = c.strip()
            if c:
                cat_map.setdefault(c, []).append((meta["title"], base))
    for cat, members in sorted(cat_map.items()):
        slug = "Category_" + cat.replace(" ", "_")
        items = "\n".join(
            f'<li><a href="{href}">{html.escape(title)}</a></li>'
            for title, href in sorted(members)
        )
        cbody = (
            f'<p>This category groups articles tagged <b>{html.escape(cat)}</b> in the '
            f'<a href="index.html">Fraud-OSINT Wiki</a>. '
            f'There {"is" if len(members)==1 else "are"} {len(members)} '
            f'{"page" if len(members)==1 else "pages"} in this category.</p>'
            f'<h2 id="pages">Pages in category &ldquo;{html.escape(cat)}&rdquo;</h2>'
            f'<ul>{items}</ul>'
            f'<p class="hatnote">See also the <a href="Index.html">full index</a> '
            f'and the <a href="Full_Report.html">single-page report</a>.</p>'
        )
        cpage = SHELL.format(
            title=f"Category: {cat}",
            desc=f"Articles in the {cat} category of the Fraud-OSINT Wiki.",
            depth="../",
            sidebar=render_sidebar(slug + ".html"),
            body=cbody,
            catlinks="",
        )
        with open(os.path.join(OUT_DIR, slug + ".html"), "w", encoding="utf-8") as f:
            f.write(cpage)
        built += 1

    # ---- copy skin into wiki/ sibling & drop .nojekyll and a root redirect ----
    # (skin referenced as ../skin/ from wiki/, so ensure it exists at site root)
    with open(os.path.join(os.path.dirname(OUT_DIR), ".nojekyll"), "w") as f:
        f.write("")
    # root index.html -> redirect into wiki/
    with open(os.path.join(os.path.dirname(OUT_DIR), "index.html"), "w", encoding="utf-8") as f:
        f.write('<!DOCTYPE html><meta charset="utf-8">'
                '<meta http-equiv="refresh" content="0; url=wiki/index.html">'
                '<title>Fraud-OSINT Wiki</title>'
                '<p>Redirecting to the <a href="wiki/index.html">Fraud-OSINT Wiki</a>&hellip;</p>')

    print(f"Built {built} pages into {OUT_DIR} (incl. Full_Report). "
          f"Report sections present: {sum(1 for s in REPORT_ORDER if s in parsed)}/{len(REPORT_ORDER)}")


if __name__ == "__main__":
    build()
