from langgraph.graph import START, StateGraph, END

from chef.graph.state import ChefState
from chef.graph.nodes import (
    NodeNames,
    summarize_if_needed,
    process_request,
    handle_deviation,
)
from chef.graph.nodes.classify_request import classify_request, HANDLE_DEVIATION


# --- Graph Construction ---

agent_builder = StateGraph(ChefState)

# Add nodes
agent_builder.add_node(NodeNames.SUMMARIZE_IF_NEEDED, summarize_if_needed)
agent_builder.add_node(NodeNames.PROCESS_REQUEST, process_request)
agent_builder.add_node(NodeNames.HANDLE_DEVIATION, handle_deviation)

# Edges: START → summarize → process → (conditional) → deviation or END
agent_builder.add_edge(START, NodeNames.SUMMARIZE_IF_NEEDED)
agent_builder.add_edge(NodeNames.SUMMARIZE_IF_NEEDED, NodeNames.PROCESS_REQUEST)

# Conditional routing from process_request
agent_builder.add_conditional_edges(
    NodeNames.PROCESS_REQUEST,
    classify_request,
    {
        HANDLE_DEVIATION: NodeNames.HANDLE_DEVIATION,
        END: END,
    },
)

agent_builder.add_edge(NodeNames.HANDLE_DEVIATION, END)

# Compile
agent = agent_builder.compile()
