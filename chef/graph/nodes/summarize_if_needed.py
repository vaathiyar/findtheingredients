import logging

from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
    AIMessage,
    RemoveMessage,
)

from chef.graph.state import ChefState
from chef.graph.chat_models import summarization_model
from chef.graph.prompts import SUMMARIZATION_PROMPT
from chef.constants import CONVERSATION_TOKEN_BUDGET

logger = logging.getLogger(__name__)


def _estimate_token_count(messages: list) -> int:
    """Rough token estimate: ~4 chars per token."""
    return sum(len(str(m.content)) for m in messages) // 4


async def summarize_if_needed(state: ChefState) -> dict:
    """Summarize and trim conversation if messages exceed token budget."""
    messages = state["messages"]
    token_estimate = _estimate_token_count(messages)

    if token_estimate <= CONVERSATION_TOKEN_BUDGET:
        return {}

    # Keep the most recent messages, summarize the rest.
    split_point = len(messages) // 2
    messages_to_summarize = messages[:split_point]

    formatted_history = "\n".join(
        f"{'User' if isinstance(m, HumanMessage) else 'Assistant'}: {m.content}"
        for m in messages_to_summarize
    )

    existing_summary = state.get("conversation_summary", "")

    prompt = SUMMARIZATION_PROMPT.format(
        messages_to_summarize=formatted_history,
        existing_summary=existing_summary or "None",
    )

    response = await summarization_model.ainvoke([SystemMessage(content=prompt)])

    logger.info(
        "Summarized %d messages (est. %d tokens over budget)",
        len(messages_to_summarize),
        token_estimate - CONVERSATION_TOKEN_BUDGET,
    )

    # Use RemoveMessage to delete summarized messages via the add_messages reducer.
    # Returning the trimmed list directly would APPEND (duplicating), not replace.
    removals = [RemoveMessage(id=m.id) for m in messages_to_summarize if m.id]

    return {
        "messages": removals,
        "conversation_summary": response.content,
    }
