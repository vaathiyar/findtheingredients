import logging

from langchain_core.messages import SystemMessage
from langgraph.types import Command

from chef.graph.state import (
    ChefState,
    ExtractAndRouteOutput,
    SimpleQueryResponse,
    StepChangeResponse,
    DeviationResponse,
)
from chef.graph.chat_models import route_model
from chef.graph.nodes.node_names import NodeNames
from chef.graph.prompts import ROUTE_PROMPT

logger = logging.getLogger(__name__)


async def extract_and_route(state: ChefState) -> Command:
    """Classifies user intent, extracts metadata, and routes to the appropriate node."""
    routing = state["routing"]

    prompt = ROUTE_PROMPT.format(
        recipe_title=state["base_recipe"].title,
        current_step=state["dish_state"]["current_step"],
    )

    raw: ExtractAndRouteOutput = await route_model.with_structured_output(
        ExtractAndRouteOutput
    ).ainvoke([SystemMessage(content=prompt)] + state["messages"])

    result = raw.result
    logger.info("extract_and_route classified as: %s", result.__class__.__name__)

    # ADR: Relying on Command for now, idk if it provides the same level of visibility and logging as conditional_edge to route the graph.
    # This means that the graph will probably look incomplete when visualizing (I don't think langgraph picks up Command triggers when building the graph).
    # But we'll deal with it when we get there (i.e. when we need visibility). Should be a simple refactor so ~~
    if isinstance(result, SimpleQueryResponse):
        return Command(goto=NodeNames.SIMPLE_QUERY_RESPONSE)

    elif isinstance(result, StepChangeResponse):
        return Command(
            goto=NodeNames.STEP_CHANGE_RESPONSE,
            update={"routing": {**routing, "new_step": result.new_step}},
        )

    else:  # DeviationResponse
        target = NodeNames.CONFIRMATION_COMPUTE if result.is_confirmation else NodeNames.NEW_PROPOSAL
        return Command(
            goto=target,
            update={"routing": {**routing, "deviation_type": result.deviation_type}},
        )
