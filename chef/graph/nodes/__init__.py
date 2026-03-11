from chef.graph.nodes.summarize_if_needed import summarize_if_needed
from chef.graph.nodes.process_request import process_request
from chef.graph.nodes.handle_deviation import handle_deviation

from enum import StrEnum


class NodeNames(StrEnum):
    SUMMARIZE_IF_NEEDED = "summarize_if_needed"
    PROCESS_REQUEST = "process_request"
    HANDLE_DEVIATION = "handle_deviation"


__all__ = [
    "NodeNames",
    "summarize_if_needed",
    "process_request",
    "handle_deviation",
]
