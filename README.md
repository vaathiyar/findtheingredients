# Sous
A plaform where you can find recipes from youtube given your available ingredients and a voice-conversational bot to help you cook the recipe.

### What's done so far
- The latter part where a voice-conversational bot helps you cook the recipe.
- The data ingestion part where the data is scraped from youtube and stored.

### What's pending
- Latency improvements on the voice agent.
- A google-type keyword search to find all youtube recipes, given the ingredients. 

#### WIP, the public repo is a bit behind.

---

## CLI Commands

Requires `uv`. All commands are run from the project root.

### Ingest a recipe from a YouTube video
```bash
uv run python main.py ingest "<youtube_url>"
```
Downloads audio, transcribes, extracts the recipe via LLM, and saves it to CockroachDB. Also writes a local JSON copy to `artifacts/outputs/<slug>.json` for debugging.

### List all ingested recipes
```bash
uv run python main.py list
```
Prints all recipes currently in the DB with their slug, title, and cuisine.

### Chat with the chef agent (text mode)
```bash
uv run python main.py chat <recipe_slug>
```
Starts an interactive text session with the chef agent for the given recipe. `recipe_slug` is the kebab-case ID shown by `list` (e.g. `ambur-chicken-biryani-vahchef`). Accepts either the slug or the UUID.

