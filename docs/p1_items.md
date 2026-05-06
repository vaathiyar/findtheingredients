# P1 — Next Phase Features

## 1. Cuisine-Preset Onboarding
Pick a kitchen profile during onboarding ("Indian kitchen", "East Asian kitchen", "Mediterranean kitchen") and auto-populate pantry staples — spices, sauces, oils typical for that cuisine. Eliminates the cold-start problem of manually adding 30 spice jars one by one.

## 2. Intent-First Search Mode
Secondary search path: user types "I want to make pasta" and results are filtered by pantry match. Pantry-first (P0) answers "what can I cook?", intent-first answers "can I cook *this*?" Needs exploration on the data side for intent-matching — likely requires dish-level or cuisine-level tagging beyond just ingredient matching.

## 3. Dish Identity / Canonical Dish Names
Group multiple recipes for the same dish ("12 butter chicken recipes") under a shared dish entity. Same canonicalization challenge as ingredients — "murgh makhani" = "butter chicken". Enables browsing by dish, comparing sources, and deduplication.

## 4. Dietary Restrictions as Profile Setting
Profile-level diet preference (vegetarian, vegan, non-veg, pescatarian) with per-search override. Default hides non-matching recipes. "Show all" toggle for cooking for guests or exploring.
