import re
from datetime import date
from html import escape, unescape
from pathlib import Path

from publisher import format_date_es

EDITIONS_DIR = Path("docs/editions")
INDEX_PATH = Path("docs/index.html")

TITLE_RE = re.compile(r"<title>(.*?)</title>", re.DOTALL)
SUMMARY_SECTION_RE = re.compile(r'<section class="summary">(.*?)</section>', re.DOTALL)
PARAGRAPH_RE = re.compile(r"<p>(.*?)</p>", re.DOTALL)

INDEX_TEMPLATE = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>El Curioso</title>
<style>
  body {{ font-family: Georgia, "Times New Roman", serif; max-width: 760px; margin: 2rem auto; padding: 0 1rem; color: #1a1a1a; }}
  header {{ text-align: center; border-bottom: 4px double #1a1a1a; margin-bottom: 1.5rem; padding-bottom: 1rem; }}
  header h1 {{ font-size: 2.5rem; margin: 0; letter-spacing: 0.05em; }}
  header .tagline {{ text-transform: uppercase; letter-spacing: 0.1em; font-size: 0.85rem; color: #555; }}
  ul {{ list-style: none; padding: 0; }}
  li {{ border-bottom: 1px solid #ccc; padding: 1rem 0; }}
  li a {{ color: inherit; text-decoration: none; font-size: 1.2rem; }}
  li a:hover {{ text-decoration: underline; }}
  li .edition-date {{ display: block; text-transform: uppercase; letter-spacing: 0.1em; font-size: 0.75rem; color: #777; margin-bottom: 0.2rem; }}
  li .summary {{ margin: 0.4rem 0 0; font-size: 0.95rem; color: #333; font-style: italic; }}
</style>
</head>
<body>
<header>
  <h1>El Curioso</h1>
  <div class="tagline">Ediciones publicadas</div>
</header>
<main>
<ul>
{editions_html}
</ul>
</main>
</body>
</html>
"""

EDITION_ITEM_TEMPLATE = """  <li>
    <span class="edition-date">{edition_date}</span>
    <a href="editions/{filename}">{title}</a>
    {summary_html}
  </li>"""

SUMMARY_PARAGRAPH_TEMPLATE = '<p class="summary">{paragraph}</p>'


def extract_title(html: str, fallback: str) -> str:
    match = TITLE_RE.search(html)
    return unescape(match.group(1).strip()) if match else fallback


def extract_summary(html: str) -> list[str]:
    section_match = SUMMARY_SECTION_RE.search(html)
    if not section_match:
        return []
    paragraphs = PARAGRAPH_RE.findall(section_match.group(1))
    return [unescape(p.strip()) for p in paragraphs]


def build_homepage(editions_dir: Path = EDITIONS_DIR, output_path: Path = INDEX_PATH) -> Path:
    editions = []
    for path in editions_dir.glob("*.html"):
        edition_date = date.fromisoformat(path.stem)
        html = path.read_text(encoding="utf-8")
        title = extract_title(html, fallback=path.stem)
        summary_paragraphs = extract_summary(html)
        editions.append((edition_date, path.name, title, summary_paragraphs))

    editions.sort(key=lambda e: e[0], reverse=True)

    editions_html = "\n".join(
        EDITION_ITEM_TEMPLATE.format(
            edition_date=escape(format_date_es(edition_date)),
            filename=escape(filename),
            title=escape(title),
            summary_html="\n    ".join(
                SUMMARY_PARAGRAPH_TEMPLATE.format(paragraph=escape(paragraph))
                for paragraph in summary_paragraphs
            ),
        )
        for edition_date, filename, title, summary_paragraphs in editions
    )

    html = INDEX_TEMPLATE.format(editions_html=editions_html)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")

    return output_path
