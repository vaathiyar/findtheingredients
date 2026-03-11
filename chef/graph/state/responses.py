from typing import Literal, Optional, Union
from pydantic import BaseModel, Field

from chef.graph.state.enums import DeviationFlag, DeviationType


class SimpleQueryResponse(BaseModel):
    """Queries, clarifications, general conversation."""

    response_message: str


class StepChangeResponse(BaseModel):
    """Step advancement or backtracking. If step-change is clear, populate new_step. Otherwise, use response_message for clarification."""

    new_step: Optional[int] = Field(
        None,
        description=("New step number if the change is clear."),
    )
    response_message: str


class DeviationResponse(BaseModel):
    """Deviation detected — routes to handle_deviation node."""

    sub_type: DeviationFlag
    deviation_type: DeviationType


class ProcessRequestOutput(BaseModel):
    result: Union[
        SimpleQueryResponse,
        StepChangeResponse,
        DeviationResponse,
    ]
