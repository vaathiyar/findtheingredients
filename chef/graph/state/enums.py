from enum import Enum


class StepStatus(Enum):
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"


class DeviationType(Enum):
    SUBSTITUTION = "substitution"
    AMENDMENT = "amendment"


class DeviationFlag(Enum):
    NEW_PROPOSAL = "new_proposal"
    CONFIRMED = "confirmed"
