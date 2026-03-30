# Conversation token budget for message trimming.
# When messages exceed this, summarize_if_needed will summarize + trim.
CONVERSATION_TOKEN_BUDGET = 8_000

# Model identifiers
CHEF_MODEL = "google_genai:gemini-3-flash-preview"
SUMMARIZATION_MODEL = "google_genai:gemini-3-flash-preview"
ROUTE_MODEL = "google_genai:gemini-3.1-flash-lite-preview"
