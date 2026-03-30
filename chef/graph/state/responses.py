from typing import Optional, Union
from pydantic import BaseModel, Field

from chef.graph.state.enums import DeviationType


class SimpleQueryResponse(BaseModel):
    """Questions, clarifications, general recipe chat."""

    pass


class StepChangeResponse(BaseModel):
    """Step advancement or backtracking."""

    new_step: Optional[int] = Field(
        None,
        description="New step number if the target is unambiguous.",
    )


class DeviationResponse(BaseModel):
    """Ingredient substitution, corrective fix, or confirming a prior proposed change."""

    deviation_type: DeviationType
    is_confirmation: bool = Field(
        False,
        description="True only when the user is confirming a previously proposed change.",
    )


class ExtractAndRouteOutput(BaseModel):
    result: Union[
        SimpleQueryResponse,
        StepChangeResponse,
        DeviationResponse,
    ]
