import json
import logging

from langchain_core.messages import AIMessage, SystemMessage

from chef.graph.state import (
    ChefState,
    ProcessRequestOutput,
    SimpleQueryResponse,
    StepChangeResponse,
    DeviationResponse,
)
from chef.graph.chat_models import chef_model
from chef.graph.prompts import SYSTEM_PROMPT

logger = logging.getLogger(__name__)


def _format_deviations_section(state: ChefState) -> str:
    deviations = state.get("deviations", [])
    if not deviations:
        return "No deviations from the base recipe so far."

    return json.dumps(
        [d.model_dump(mode="json") for d in deviations],
        indent=2,
    )


def _format_conversation_summary_section(state: ChefState) -> str:
    summary = state.get("conversation_summary", "")
    if not summary:
        return ""
    return f"## Earlier Conversation Summary\n{summary}"


def _build_system_prompt(state: ChefState) -> str:
    recipe = state["base_recipe"]
    dish = state["dish_state"]

    return SYSTEM_PROMPT.format(
        recipe_title=recipe.title,
        current_step=dish["current_step"],
        total_steps=len(recipe.steps),
        step_status=dish["step_status"].value,
        deviations_section=_format_deviations_section(state),
        conversation_summary_section=_format_conversation_summary_section(state),
        base_recipe=recipe.model_dump_json(indent=2),
    )


def process_request(state: ChefState) -> dict:
    """Main reasoning node. Classifies user intent and responds or flags for routing."""
    system_prompt = _build_system_prompt(state)

    model_with_structure = chef_model.with_structured_output(ProcessRequestOutput)

    raw: ProcessRequestOutput = model_with_structure.invoke(
        [SystemMessage(content=system_prompt)] + state["messages"]
    )

    response = raw.result

    logger.info("process_request classified as: %s", response.__class__.__name__)

    result: dict = {}

    if isinstance(response, SimpleQueryResponse):
        result["response_message"] = response.response_message
        result["messages"] = [AIMessage(content=response.response_message)]

    elif isinstance(response, StepChangeResponse):
        result["response_message"] = response.response_message
        result["messages"] = [AIMessage(content=response.response_message)]
        if response.new_step is not None:
            result["dish_state"] = {
                **state["dish_state"],
                "current_step": response.new_step,
            }

    elif isinstance(response, DeviationResponse):
        result["routing"] = {
            "deviation_flag": response.sub_type,
            "deviation_type": response.deviation_type,
        }

    return result
