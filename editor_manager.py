from agents import gen_trace_id, trace

from homepage import build_homepage
from publisher import build_newspaper
from reader import get_news_articles
from rewriter import rewrite_articles
from summarizer import summarize_articles

class EditorManager:

    async def run(self):
        """ Run the editor process"""
        trace_id = gen_trace_id()
        with trace("Editor trace", trace_id=trace_id):
            yield f"Starting editor process with trace ID {trace_id}"

            yield f"Reading RSS feed..."
            articles = get_news_articles()

            yield f"Rewriting {len(articles)} articles..."
            rewritten_articles = await rewrite_articles(articles)

            yield f"Creating summary..."
            summary = await summarize_articles(rewritten_articles)

            yield f"Summary created:\nTitle: {summary.title}\nContent: {summary.content}"

            yield "Building newspaper..."
            output_path = build_newspaper(rewritten_articles, summary)

            yield f"Newspaper published to {output_path}"

            yield "Updating homepage..."
            build_homepage()

            yield "Homepage updated."