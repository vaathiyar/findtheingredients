from enum import Enum


class StepStatus(Enum):
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"


class DeviationType(Enum):
    SUBSTITUTION = "substitution"
    AMENDMENT = "amendment"


