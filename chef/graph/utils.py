import json

from chef.graph.state import ChefState
from chef.graph.prompts import SYSTEM_PROMPT


def format_deviations(state: ChefState, empty: str = "None") -> str:
    deviations = state.get("deviations", [])
    if not deviations:
        return empty

    return json.dumps(
        [d.model_dump(mode="json") for d in deviations],
        indent=2,
    )


def build_system_prompt(state: ChefState) -> str:
    recipe = state["base_recipe"]
    dish = state["dish_state"]
    summary = state.get("conversation_summary", "")
    summary_section = f"## Earlier Conversation Summary\n{summary}" if summary else ""

    return SYSTEM_PROMPT.format(
        recipe_title=recipe.title,
        current_step=dish["current_step"],
        total_steps=len(recipe.steps),
        step_status=dish["step_status"].value,
        deviations_section=format_deviations(
            state, empty="No deviations from the base recipe so far."
        ),
        conversation_summary_section=summary_section,
        base_recipe=recipe.model_dump_json(indent=2),
    )
