from langgraph.graph import StateGraph, END

from graph.state import AgentState
from graph.nodes.ingest import ingest_node
from graph.nodes.understand import understand_node
from graph.nodes.recall_check import recall_check_node, route_after_recall
from graph.nodes.apply import apply_node


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("ingest", ingest_node)
    graph.add_node("understand", understand_node)
    graph.add_node("recall_check", recall_check_node)
    graph.add_node("apply", apply_node)

    graph.set_entry_point("ingest")
    graph.add_edge("ingest", "understand")
    graph.add_edge("understand", "recall_check")
    graph.add_conditional_edges(
        "recall_check",
        route_after_recall,
        {"retry": "understand", "proceed": "apply"},
    )
    graph.add_edge("apply", END)

    return graph.compile()
