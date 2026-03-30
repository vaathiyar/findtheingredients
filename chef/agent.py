from langgraph.graph import START, StateGraph, END

from chef.graph.state import ChefState
from chef.graph.nodes import (
    NodeNames,
    summarize_if_needed,
    extract_and_route,
    simple_query_response,
    step_change_response,
    new_proposal,
    confirmation_compute,
    confirmation_ack,
)


# --- Graph Construction ---

agent_builder = StateGraph(ChefState)

# Add nodes
agent_builder.add_node(NodeNames.SUMMARIZE_IF_NEEDED, summarize_if_needed)
agent_builder.add_node(NodeNames.EXTRACT_AND_ROUTE, extract_and_route)
agent_builder.add_node(NodeNames.SIMPLE_QUERY_RESPONSE, simple_query_response)
agent_builder.add_node(NodeNames.STEP_CHANGE_RESPONSE, step_change_response)
agent_builder.add_node(NodeNames.NEW_PROPOSAL, new_proposal)
agent_builder.add_node(NodeNames.CONFIRMATION_COMPUTE, confirmation_compute)
agent_builder.add_node(NodeNames.CONFIRMATION_ACK, confirmation_ack)

# Fixed path: START → summarize → route (route uses Command to goto response node)
agent_builder.add_edge(START, NodeNames.SUMMARIZE_IF_NEEDED)
agent_builder.add_edge(NodeNames.SUMMARIZE_IF_NEEDED, NodeNames.EXTRACT_AND_ROUTE)

# Terminal edges for single-node response paths
agent_builder.add_edge(NodeNames.SIMPLE_QUERY_RESPONSE, END)
agent_builder.add_edge(NodeNames.STEP_CHANGE_RESPONSE, END)
agent_builder.add_edge(NodeNames.NEW_PROPOSAL, END)

# Deviation confirmation path: compute state first, then stream ack
agent_builder.add_edge(NodeNames.CONFIRMATION_COMPUTE, NodeNames.CONFIRMATION_ACK)
agent_builder.add_edge(NodeNames.CONFIRMATION_ACK, END)

# Compile
chef_agent = agent_builder.compile()
