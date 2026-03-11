from typing import Optional
from typing_extensions import TypedDict
from pydantic import BaseModel, Field

from chef.graph.state.enums import StepStatus, DeviationType, DeviationFlag


class DishState(TypedDict):
    current_step: int  # 0 = pre-cook, 1+ = recipe steps
    step_status: StepStatus


class ImpactedStep(BaseModel):
    step_number: int
    impact_description: str


class Deviation(BaseModel):
    deviation_type: DeviationType
    introduced_step: int
    reason: str
    description: str
    swapped_ingredients: Optional[dict[str, str]] = Field(
        None,
        description="Ingredient swaps (original → substitute). None for amendments.",
    )
    impacted_steps: list[ImpactedStep] = Field(
        default_factory=list,
        description="Steps affected by this deviation, with descriptions of impact.",
    )


class RoutingContext(TypedDict):
    # ADR: Created this to explicitly separate intermediate routing data that does not belong to the core business state.

    deviation_flag: Optional[DeviationFlag]
    deviation_type: Optional[DeviationType]
