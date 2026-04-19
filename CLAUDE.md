# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Sous** is an AI cooking assistant that:
1. Ingests cooking YouTube videos → downloads audio → transcribes → extracts structured recipes
2. Provides an interactive chef agent to guide users through the extracted recipe step-by-step

## Commands

Uses `uv` for dependency management and Python 3.13.

```bash
# Run the ingest pipeline on a YouTube URL
uv run python main.py ingest "<youtube_url>"

# Chat with the chef agent over a pre-ingested recipe
uv run python main.py chat artifacts/outputs/<recipe>.json

# Add a dependency
uv add <package>
```

No test suite exists yet. Run the app directly to verify behavior.

## Architecture

### Two-Pipeline Design

**Pipeline 1: `recipe_ingest/`** — One-shot ingestion
- `recipe_ingest/agent.py`: LangGraph graph: `transcribe_recipe_audio` → `extract_recipe_from_transcript` → END
- `recipe_ingest/services/youtube.py`: Downloads audio via `yt-dlp`, fetches video metadata
- `recipe_ingest/services/transcription/sarvam.py`: Transcribes audio via Sarvam AI (multilingual, handles Tamil etc.)
- Output: JSON saved to `artifacts/outputs/<title>.json`

**Pipeline 2: `chef/`** — Stateful conversation loop
- `chef/agent.py`: LangGraph graph: `summarize_if_needed` → `process_request` → (conditional) → `handle_deviation` or END
- `chef/graph/state/chef_state.py`: `ChefState` TypedDict — tracks `base_recipe`, `dish_state` (current step + status), `deviations`, `messages`, `routing`, `response_message`
- `chef/graph/nodes/classify_request.py`: Routing logic — decides if user message is a deviation or normal
- Deviation = when user does something different from the recipe (different ingredient, skipped step, etc.)

**Shared**
- `shared/schemas/recipe.py`: Core data model — `ExtractedRecipe`, `Step`, `StepIngredient`, etc. Used by both pipelines.
- `shared/constants.py`: `ARTIFACTS_DIR = "artifacts"`

### Key Data Flow
```
YouTube URL
  → fetch_metadata() + download audio
  → Sarvam transcription
  → LLM extraction → ExtractedRecipe (structured)
  → saved to artifacts/outputs/*.json
  → loaded by chef agent
  → stateful conversation (ChefState tracks step progress + deviations)
```

### LLM Stack
- `langchain-google-genai` (Gemini) for recipe extraction and chef responses
- `langgraph` for agent graph orchestration
- Model configs live in `chef/graph/chat_models.py` and `recipe_ingest/graph/chat_models.py`

## Rules

- Never read `.env`, `.env.local`, `.env.*`, or any secrets/credentials files.

## Agent Rules

`.agents/rules/senior-staff-engineer.md` is loaded as an always-on rule. Before implementing any change:
- Ask whether it's a BIG or SMALL change
- Review architecture, code quality, tests, and performance in that order
- Do not implement until the user approves the direction
