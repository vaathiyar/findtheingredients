# FS — Straightforward Full-Stack Items

## 1. Almost-Cookable Recipe Filtering
Group search results by match score into buckets: "Ready to cook", "Need 1 more thing", "Need 2-3 more". Simple filter/sort on the missing-ingredient count already computed by the search algorithm. Frontend grouping + backend sort parameter.

## 2. Recipe Ingestion Jobs (URL / Channel)
User submits a YouTube URL or channel link. Backend job downloads audio, transcribes, extracts structured recipe, and adds it to the corpus. Bulk channel ingestion for seeding the corpus. Existing `recipe_ingest/` pipeline handles single URLs — extend to accept channel URLs and queue multiple ingestions.

## 3. Search Filters: Cuisine, Diet, Cook Time, Source
Standard faceted filtering on recipe metadata fields. Each is a direct lookup on indexed fields — cuisine (enum/tag), diet (veg/non-veg/vegan derived from ingredients), cook time (range), source/channel (foreign key). No algorithmic complexity, just query parameters and UI controls.
