import asyncio
import os

from agents import Agent, Runner
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from reader import NewsArticle

load_dotenv()
MODEL_NAME = os.getenv("MODEL_NAME_REWRITER") or os.getenv("MODEL_NAME")

class RewriterInput(BaseModel):
    title: str = Field(description="The original title of the news article")
    content: str = Field(description="The original body content of the news article")

class NewsArticleTranslated(BaseModel):
    title: str = Field(description="The title of the news article, simplified to A1-level Spanish")
    content: str = Field(description="The full body content of the news article, simplified to A1-level Spanish")

INSTRUCTIONS = """
You are a writer for "El Curioso", a daily newspaper that helps Spanish
language learners practice reading. Each article you receive is real news
sourced from El País, written in standard Spanish. Your job is to rewrite it
so a learner at CEFR A2 level can read and understand it.

Follow these rules:
- Simplify vocabulary: use common, everyday words and avoid idioms, jargon, and
  rare terms.
- Use short, simple sentences with basic grammar (present, preterite, and near
  future tenses only). Avoid subjunctive, complex subordinate clauses, and
  passive voice.
- You may shorten the text and drop secondary details if needed to keep it
  simple, but keep the core facts (who, what, when, where) intact.
- Keep the output in Spanish. Do not translate to another language.
- Rewrite both the title and the content, following the same rules.
"""



async def rewrite_articles(articles: list[NewsArticle]) -> list[NewsArticle]:
    inputs = [RewriterInput(title=article.title, content=article.content) for article in articles]

    rewriter_agent = Agent(name="Rewriter", instructions=INSTRUCTIONS, model=MODEL_NAME, output_type=NewsArticleTranslated)
    runners = [Runner.run(rewriter_agent, article.model_dump_json()) for article in inputs]
    responses = await asyncio.gather(*runners)

    return [
        article.model_copy(update={"title": response.final_output.title, "content": response.final_output.content})
        for article, response in zip(articles, responses)
    ]