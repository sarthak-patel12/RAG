# models/langgraph_graph.py
from langgraph.graph import StateGraph, END
from models.langgraph_nodes import ConversationState, retrieve, generate_answer

def build_langgraph_app():
    """Build and return a compiled LangGraph app for conversation processing."""
    workflow = StateGraph(ConversationState)

    workflow.add_node("retrieve", retrieve)
    workflow.add_node("generate", generate_answer)

    workflow.set_entry_point("retrieve")
    workflow.add_edge("retrieve", "generate")
    workflow.add_edge("generate", END)

    return workflow.compile()


app = build_langgraph_app()