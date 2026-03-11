import logging

from langgraph.graph import END

from chef.graph.state import ChefState

logger = logging.getLogger(__name__)

HANDLE_DEVIATION = "handle_deviation"


def classify_request(state: ChefState) -> str:
    """Pure routing node. No LLM call.

    Routes to handle_deviation if a deviation was flagged,
    otherwise to END (response_message should already be set).
    """
    routing = state.get("routing") or {}

    if routing.get("deviation_flag") is not None:
        logger.info(
            "Routing to deviation node: flag=%s, type=%s",
            routing["deviation_flag"].value,
            routing.get("deviation_type", "unknown"),
        )
        return HANDLE_DEVIATION

    if not state.get("response_message"):
        logger.error(
            "classify_request: no deviation_flag and no response_message — "
            "this should not happen. Routing to END."
        )

    return END
