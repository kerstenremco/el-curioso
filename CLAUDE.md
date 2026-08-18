# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

El Curioso is a daily-newspaper generator for Spanish language learners. It pulls recent articles from an El País RSS feed, uses LLM agents to rewrite them at CEFR A2 level, generates a front-page summary, and renders everything into a static HTML page.

## Commands

This project uses `uv` for dependency management (Python >=3.12).

- Install dependencies: `uv sync`
- Run the pipeline: `uv run main.py`

There is no test suite, linter, or formatter configured in this repo.

## Configuration

Runtime config is read from a `.env` file (via `python-dotenv`), not committed to git:

- `OPENAI_API_KEY` — required by the `openai-agents` SDK.
- `MODEL_NAME` — default model used by both agent stages.
- `MODEL_NAME_REWRITER` / `MODEL_NAME_SUMMARIZER` — optional per-stage overrides (each falls back to `MODEL_NAME` if unset).

## Architecture

The pipeline is a straight-line async sequence, orchestrated by `EditorManager.run()` in `editor_manager.py`, which yields progress strings as it goes (consumed by `main.py`'s `async for` loop). Each stage lives in its own module and passes typed data (Pydantic `BaseModel`s) to the next:

1. **`reader.py`** — fetches and parses the El País RSS and filters to articles published within `MAX_ARTICLE_AGE` (24h). Produces `NewsArticle` objects.
2. **`rewriter.py`** — runs one `openai-agents` `Agent` per article **concurrently** (`asyncio.gather`) to rewrite title+content into simple A2-level Spanish, using a structured `output_type` (`NewsArticleTranslated`). Returns updated `NewsArticle` copies (`model_copy(update=...)`), preserving all original metadata (links, images, dates).
3. **`summarizer.py`** — runs a single `Agent` over all rewritten articles to produce one front-page `NewsSummary` (title + short overview) in A2 Spanish.
4. **`publisher.py`** — renders the rewritten articles and summary into a self-contained HTML file using templates.

Key conventions:

- Agent `INSTRUCTIONS` are hardcoded prompt strings per module; both currently target CEFR A2-level Spanish output — keep prompt and docstring language level claims in sync if changed.
- The `openai-agents` SDK's `trace(...)` context manager wraps the whole pipeline run in `editor_manager.py` for tracing/observability; new stages added to the pipeline should run inside this trace.
