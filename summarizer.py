import os

from agents import Agent, Runner
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from reader import NewsArticle

load_dotenv()
MODEL_NAME = os.getenv("MODEL_NAME_SUMMARIZER") or os.getenv("MODEL_NAME")

class SummarizerArticleInput(BaseModel):
    title: str = Field(description="The original title of the news article")
    content: str = Field(description="The original body content of the news article")

class SummarizerInput(BaseModel):
    articles: list[SummarizerArticleInput] = Field(description="The news articles to summarize")

class NewsSummary(BaseModel):
    title: str = Field(description="A short title covering the overall content of the summary")
    content: str = Field(description="A summary covering the key points of all the given news articles")

INSTRUCTIONS = """
You are a writer for "El Curioso", a daily newspaper that helps Spanish
language learners practice reading. You are given several news articles
already rewritten in simple, CEFR A2-level Spanish. Write a single front-page
summary in Spanish that gives readers an overview of today's news before they
dive into the full articles.

Follow these rules:
- Highlight the most important facts.
- Write at CEFR A2 level: common vocabulary, short sentences, basic grammar
  (present, preterite, and near future tenses only), no idioms or jargon.
- Keep the summary concise, using a maximum of three paragraphs.
- Write a short title that reflects the overall content of the summary.
- Keep the output in Spanish. Do not translate to another language.
"""



async def summarize_articles(articles: list[NewsArticle]) -> NewsSummary:
    input_data = SummarizerInput(
        articles=[SummarizerArticleInput(title=article.title, content=article.content) for article in articles]
    )

    summarizer_agent = Agent(name="Summarizer", instructions=INSTRUCTIONS, model=MODEL_NAME, output_type=NewsSummary)
    response = await Runner.run(summarizer_agent, input_data.model_dump_json())

    return response.final_output
