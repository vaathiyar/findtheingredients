import logging

from langchain_core.messages import AIMessage, SystemMessage

from chef.graph.state import (
    ChefState,
    Deviation,
    DeviationFlag,
)
from chef.graph.chat_models import chef_model
from chef.graph.prompts import NEW_DEVIATION_PROMPT, CONFIRM_DEVIATION_PROMPT
from chef.graph.utils import format_deviations

logger = logging.getLogger(__name__)


class DeviationNodeOutput(Deviation):
    """Extends Deviation with fields only needed for the LLM response."""

    response_message: str
    is_genuine_deviation: bool


def handle_deviation(state: ChefState) -> dict:
    """Deviation handling node. Proposes new deviations or finalizes confirmed ones."""
    routing = state["routing"]
    deviation_flag = routing["deviation_flag"]
    deviation_type = routing.get("deviation_type")
    recipe = state["base_recipe"]
    dish = state["dish_state"]

    prior_deviations = format_deviations(state)

    if deviation_flag == DeviationFlag.NEW_PROPOSAL:
        prompt = NEW_DEVIATION_PROMPT.format(
            recipe_title=recipe.title,
            current_step=dish["current_step"],
            total_steps=len(recipe.steps),
            deviation_type=deviation_type.value if deviation_type else "unknown",
            prior_deviations=prior_deviations,
            base_recipe=recipe.model_dump_json(indent=2),
        )

        # For new proposals, we just need a text response (the proposal).
        # No structured deviation yet — that comes on confirmation.
        response = chef_model.invoke(
            [SystemMessage(content=prompt)] + state["messages"]
        )

        logger.info("Deviation proposal generated")

        return {
            "response_message": response.content,
            "messages": [AIMessage(content=response.content)],
            # Clear routing flags after handling
            "routing": {"deviation_flag": None, "deviation_type": None},
        }

    elif deviation_flag == DeviationFlag.CONFIRMED:
        prompt = CONFIRM_DEVIATION_PROMPT.format(
            recipe_title=recipe.title,
            current_step=dish["current_step"],
            total_steps=len(recipe.steps),
            deviation_type=deviation_type.value if deviation_type else "unknown",
            prior_deviations=prior_deviations,
            base_recipe=recipe.model_dump_json(indent=2),
        )

        model_with_structure = chef_model.with_structured_output(DeviationNodeOutput)

        response = model_with_structure.invoke(
            [SystemMessage(content=prompt)] + state["messages"]
        )

        logger.info("Deviation confirmed and computed")

        result: dict = {
            "response_message": response.response_message,
            "messages": [AIMessage(content=response.response_message)],
            # Clear routing flags
            "routing": {"deviation_flag": None, "deviation_type": None},
        }

        # Only add to deviations if it was genuinely a deviation
        if response.is_genuine_deviation:
            new_deviation = Deviation(
                deviation_type=response.deviation_type,
                introduced_step=response.introduced_step,
                reason=response.reason,
                description=response.description,
                swapped_ingredients=response.swapped_ingredients,
                impacted_steps=response.impacted_steps,
            )
            result["deviations"] = state.get("deviations", []) + [new_deviation]

        return result

    else:
        logger.error("handle_deviation called with unexpected flag: %s", deviation_flag)
        return {
            "routing": {"deviation_flag": None, "deviation_type": None},
        }
