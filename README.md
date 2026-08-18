# El Curioso

[![Read El Curioso](https://img.shields.io/badge/read-el%20curioso-b3352c?style=for-the-badge)](https://kerstenremco.github.io/el-curioso/)

A small daily "newspaper" that rewrites Spanish news at an easier reading
level, built as a personal project to learn **agentic AI** — using the
[OpenAI Agents SDK](https://github.com/openai/openai-agents-python) to chain
LLM agents into a working pipeline.

[![Latest edition](https://img.shields.io/github/last-commit/kerstenremco/el-curioso?path=docs&label=latest%20edition)](https://kerstenremco.github.io/el-curioso/)
[![Publish newspaper](https://github.com/kerstenremco/el-curioso/actions/workflows/publish.yml/badge.svg)](https://github.com/kerstenremco/el-curioso/actions/workflows/publish.yml)

## What it does

El Curioso pulls recent articles from an [El País](https://elpais.com/) RSS
feed and runs them through a small pipeline of LLM agents:

1. **Read** — fetch and parse the RSS feed, keep only recent articles.
2. **Rewrite** — simplify each article's title and content to CEFR A2-level
   Spanish (short sentences, common vocabulary, basic grammar).
3. **Summarize** — write a short front-page summary covering all of today's
   articles.
4. **Publish** — render everything into a static HTML "edition" and update a
   homepage listing all published editions.

The result is a static site meant for Spanish learners who want to read real
news without getting lost in advanced vocabulary and grammar.

## Source & disclaimer

Article content is sourced from [El País](https://elpais.com/) and
rewritten/summarized by an LLM for language-learning purposes. This project
is **not affiliated with or endorsed by El País**, and the generated content
is intended **for personal, educational use only** — not for redistribution
or commercial use. All rights to the original articles remain with El País.
