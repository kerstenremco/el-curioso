from datetime import date, datetime
from email.utils import parsedate_to_datetime
from html import escape
from pathlib import Path

from reader import NewsArticle
from summarizer import NewsSummary

OUTPUT_DIR = Path("docs/editions")

SPANISH_MONTHS = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]


def format_date_es(value: date, with_time: bool = False) -> str:
    formatted = f"{value.day} de {SPANISH_MONTHS[value.month - 1]} de {value.year}"
    if with_time:
        formatted += f", {value.strftime('%H:%M')}"
    return formatted

PAGE_TEMPLATE = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
  body {{ font-family: Georgia, "Times New Roman", serif; max-width: 760px; margin: 2rem auto; padding: 0 1rem; color: #1a1a1a; }}
  header {{ text-align: center; border-bottom: 4px double #1a1a1a; margin-bottom: 1.5rem; padding-bottom: 1rem; }}
  header h1 {{ font-size: 2.5rem; margin: 0; letter-spacing: 0.05em; }}
  header .date {{ text-transform: uppercase; letter-spacing: 0.1em; font-size: 0.85rem; color: #555; }}
  .summary {{ font-style: italic; border-bottom: 1px solid #ccc; padding-bottom: 1.5rem; margin-bottom: 1.5rem; }}
  .summary h2 {{ font-style: normal; }}
  article {{ margin-bottom: 2rem; }}
  article img {{ max-width: 100%; height: auto; display: block; margin-bottom: 0.5rem; }}
  article .credit {{ font-size: 0.75rem; color: #777; margin-top: -0.4rem; margin-bottom: 0.5rem; }}
  article h3 {{ margin-bottom: 0.3rem; }}
  article .pub-date {{ font-size: 0.8rem; color: #777; margin: 0 0 0.5rem; }}
  article a {{ color: inherit; }}
</style>
</head>
<body>
<header>
  <h1>El Curioso</h1>
  <div class="date">{date}</div>
</header>
<section class="summary">
  <h2>{summary_title}</h2>
  <p>{summary_content}</p>
</section>
<main>
{articles_html}
</main>
</body>
</html>
"""

ARTICLE_TEMPLATE = """<article>
  <h3><a href="{link}">{title}</a></h3>
  <p class="pub-date">{pub_date}</p>
  {image_html}
  <p>{content}</p>
</article>"""

IMAGE_TEMPLATE = """<img src="{src}" alt="{alt}">
  {credit_html}"""


def render_paragraphs(text: str) -> str:
    return "</p>\n  <p>".join(escape(p.strip()) for p in text.split("\n") if p.strip())


def render_article(article: NewsArticle) -> str:
    image_html = ""
    if article.media_thumbnail:
        credit_html = f'<div class="credit">{escape(article.media_credit)}</div>' if article.media_credit else ""
        image_html = IMAGE_TEMPLATE.format(
            src=escape(article.media_thumbnail),
            alt=escape(article.media_title or article.title),
            credit_html=credit_html,
        )

    pub_date = format_date_es(parsedate_to_datetime(article.pubDate), with_time=True)

    return ARTICLE_TEMPLATE.format(
        link=escape(article.link),
        title=escape(article.title),
        pub_date=escape(pub_date),
        image_html=image_html,
        content=render_paragraphs(article.content),
    )


def build_newspaper(articles: list[NewsArticle], summary: NewsSummary) -> Path:
    now = datetime.now()
    html = PAGE_TEMPLATE.format(
        title=escape(summary.title),
        date=format_date_es(now),
        summary_title=escape(summary.title),
        summary_content=render_paragraphs(summary.content),
        articles_html="\n".join(render_article(article) for article in articles),
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / f"{now.strftime('%Y-%m-%d')}.html"
    output_path.write_text(html, encoding="utf-8")

    return output_path
