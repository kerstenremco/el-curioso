import re
from datetime import date
from html import escape, unescape
from pathlib import Path

from publisher import format_date_es

EDITIONS_DIR = Path("docs/editions")
INDEX_PATH = Path("docs/index.html")

TITLE_RE = re.compile(r"<title>(.*?)</title>", re.DOTALL)

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
  </li>"""


def extract_title(html: str, fallback: str) -> str:
    match = TITLE_RE.search(html)
    return unescape(match.group(1).strip()) if match else fallback


def build_homepage(editions_dir: Path = EDITIONS_DIR, output_path: Path = INDEX_PATH) -> Path:
    editions = []
    for path in editions_dir.glob("*.html"):
        edition_date = date.fromisoformat(path.stem)
        title = extract_title(path.read_text(encoding="utf-8"), fallback=path.stem)
        editions.append((edition_date, path.name, title))

    editions.sort(key=lambda e: e[0], reverse=True)

    editions_html = "\n".join(
        EDITION_ITEM_TEMPLATE.format(
            edition_date=escape(format_date_es(edition_date)),
            filename=escape(filename),
            title=escape(title),
        )
        for edition_date, filename, title in editions
    )

    html = INDEX_TEMPLATE.format(editions_html=editions_html)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")

    return output_path
