# P0 — Base Feature: Recipe Discovery by Pantry

Users tell us what ingredients they have. We show them recipes they can cook, ranked by how well their pantry matches.

---

## 1. Persistent Pantry

Users maintain a saved pantry — a list of ingredients they currently have on hand. Separate screen/section in the app, editable at any time. Add items, remove items. No quantities, no expiry, no auto-depletion.

Secondary path: ad-hoc search ("I have X, Y, Z — what can I make?") without modifying the saved pantry.

## 2. Ingredient Tier Classification

Not all ingredients are equal. We need to decide what the user must explicitly declare vs what we can assume.

**Two tiers for P0:**

| Tier | Examples | Behavior |
|------|----------|----------|
| **Universal staples** | Salt, water, black pepper | Assumed. Never count as missing. |
| **Everything else** | All other ingredients | Must be in user's pantry to count as a match. |

The universal staples list must be very conservative. Items like cooking oil are **not** universal — mustard oil vs olive oil vs sesame oil changes the dish. If in doubt, don't assume it.

Cuisine-preset onboarding (P1) will later let users bulk-declare their pantry staples by kitchen type, but for P0, users manually add everything beyond the minimal universal list.

**Equipment:** Out of scope for P0. Assume the user has standard kitchen equipment.

## 3. Ingredient Canonicalization

Every ingredient in every recipe maps to a **canonical ingredient ID**. Multilingual aliases resolve to the same canonical — "vengayam" (Tamil), "pyaaz" (Hindi), "onion" (English) all map to `ingredient:onion`.

During recipe ingestion, the LLM maps extracted ingredient names to existing canonicals or creates new ones. The alias table grows with each ingested recipe.

Users search/input in any language and it resolves to the canonical.

**Taxonomy seeding:** LLM-generated base taxonomy from known ingredient databases. Grows organically during ingestion.

## 4. Substitution Groups

**Open question: does substitution matching complicate the search algorithm?**

The concern is valid. Two options:

**Option A — P0 keeps it simple.** Match on exact canonical ingredients only. If a recipe needs chicken thigh and you have chicken breast, it counts as "missing." Substitution awareness deferred to P1.

**Option B — Lightweight substitution in P0.** Substitution groups are a static lookup table (chicken thigh <-> chicken breast <-> chicken leg). During scoring, a substitutable ingredient counts as "partial match" (e.g., 0.5 instead of 1.0) rather than fully missing. The search algorithm itself doesn't change — it's still "score each recipe by pantry overlap" — the only difference is the per-ingredient scoring function checks the substitution table before marking something as missing.

**Lean: Option B is low complexity if substitution groups are a flat lookup, not a graph.** But worth prototyping to confirm.

## 5. Pantry-First Search & Ranking

**Primary search mode:** User opens the app, sees recipes ranked by pantry match. No query needed — the pantry *is* the query.

**Ranking: fewest missing ingredients.** For each recipe, compute:
- How many of its key ingredients the user has (exact match)
- How many are substitutable (if Option B above)
- How many are missing entirely

Primary sort: fewest missing. Tiebreaker: TBD (recency, popularity, or random for now).

---

## Open Questions (to resolve before implementation)

1. **Substitution groups — Option A or B?** Need to prototype the scoring to see if the substitution table lookup adds meaningful latency or complexity.
2. **Universal staples list — what's on it?** Need a concrete, conservative list. Starting point: salt, water, black pepper. Maybe sugar. Probably not oil, not flour, not garlic.
3. **Canonical taxonomy bootstrapping — how big is the seed?** Need to scope the initial ingredient taxonomy. 200 ingredients? 500? 1000? Determines effort for the LLM seeding job.
