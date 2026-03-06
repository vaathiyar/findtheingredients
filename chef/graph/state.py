from typing import Literal, Optional
from typing_extensions import TypedDict, Annotated
from langchain.messages import AnyMessage
from enum import Enum
import operator

from shared.schemas.recipe import ExtractedRecipe


class StepStatus(Enum):
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"


class DishState(TypedDict):
    current_step: int
    step_status: StepStatus


class StepDeviation(TypedDict):
    step_number: int
    reason: str
    swapped_ingredients: Optional[dict[str, str]]
    description: str


class StepChange(TypedDict):
    from_step: int
    to_step: int
    description: str


class ActiveInteraction(TypedDict):
    interaction_type: Optional[Literal["step_change", "step_deviation"]]
    active_interaction: Optional[StepChange | StepDeviation]


class ConversationHistory(TypedDict):
    previous_messages: Annotated[list[AnyMessage], operator.add]
    concatenated_summary: str


class ChefState(TypedDict):
    base_recipe: ExtractedRecipe
    dish_state: DishState
    active_interaction: ActiveInteraction
    deviations: list[StepDeviation]
    conversation_history: ConversationHistory
    context_note: str
    response_message: str
