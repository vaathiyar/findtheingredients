import json
import logging

from langchain_core.messages import AIMessage, SystemMessage

from chef.graph.state import (
    ChefState,
    Deviation,
    DeviationFlag,
)
from chef.graph.chat_models import chef_model

logger = logging.getLogger(__name__)

NEW_DEVIATION_PROMPT = """\
You are analyzing a potential recipe deviation. The user may need a substitution \
(ingredient swap) or an amendment (corrective action, timing change, addition).

## Context
Recipe: {recipe_title}
Current step: {current_step} of {total_steps}
Detected deviation type: {deviation_type}

## Prior Deviations
{prior_deviations}

## Base Recipe
{base_recipe}

## Instructions
1. First, confirm whether this is genuinely a deviation from the recipe. \
If the user's message is actually a question or step change that was misclassified, \
say so and respond to it directly instead.

2. If it IS a deviation, propose it clearly:
   - What would change
   - Which steps are affected
   - Any tradeoffs (taste, texture, technique changes)
   - Ask the user if they want to proceed

Keep your response concise and conversational — the user is cooking hands-free and your response will be voiced.
"""

CONFIRM_DEVIATION_PROMPT = """\
The user has confirmed a previously proposed deviation. Based on the conversation \
history, reconstruct the deviation and compute its full impact.

## Context
Recipe: {recipe_title}
Current step: {current_step} of {total_steps}
Deviation type: {deviation_type}

## Prior Deviations (already applied)
{prior_deviations}

## Base Recipe
{base_recipe}

## Instructions
1. Identify the deviation that was proposed and confirmed from the conversation history.
2. Compute which downstream steps are affected and HOW they are affected, \
considering all prior deviations (not just the base recipe).
3. Respond with a brief acknowledgment and mention any steps you'll adjust.

You MUST respond with a structured Deviation object AND a response message.
"""


class DeviationNodeOutput(Deviation):
    """Extends Deviation with fields only needed for the LLM response."""

    response_message: str
    is_genuine_deviation: bool


def _format_prior_deviations(state: ChefState) -> str:
    deviations = state.get("deviations", [])
    if not deviations:
        return "None"

    return json.dumps(
        [d.model_dump(mode="json") for d in deviations],
        indent=2,
    )


def handle_deviation(state: ChefState) -> dict:
    """Deviation handling node. Proposes new deviations or finalizes confirmed ones."""
    routing = state["routing"]
    deviation_flag = routing["deviation_flag"]
    deviation_type = routing.get("deviation_type")
    recipe = state["base_recipe"]
    dish = state["dish_state"]

    prior_deviations = _format_prior_deviations(state)

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
