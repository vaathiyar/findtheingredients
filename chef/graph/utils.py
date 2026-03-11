import json

from chef.graph.state import ChefState


def format_deviations(state: ChefState, empty: str = "None") -> str:
    deviations = state.get("deviations", [])
    if not deviations:
        return empty

    return json.dumps(
        [d.model_dump(mode="json") for d in deviations],
        indent=2,
    )
