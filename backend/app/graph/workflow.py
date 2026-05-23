"""LangGraph workflow wiring the three data agents + Supervisor.

Topology:

    START ─┬─► fundamentals ─┐
           ├─► social_media ─┼─► supervisor ─► END
           └─► news         ─┘

Data agents run in parallel; LangGraph fans in to the Supervisor automatically
when all selected agents have written to `agent_results`.
"""

from __future__ import annotations

from datetime import datetime

from langgraph.graph import END, START, StateGraph

from app.agents.fundamentals_agent import FundamentalsAgent
from app.agents.news_agent import NewsAgent
from app.agents.social_media_agent import SocialMediaAgent
from app.agents.supervisor_agent import SupervisorAgent
from app.graph.state import AnalysisState
from app.models.schemas import AgentName, AnalysisResponse


def _build_graph() -> "StateGraph":
    fundamentals = FundamentalsAgent()
    social = SocialMediaAgent()
    news = NewsAgent()
    supervisor = SupervisorAgent()

    # each node runs each agent asynchornously and returns the result to an array
    async def fundamentals_node(state: AnalysisState) -> dict:
        result = await fundamentals.run(state["ticker"])
        return {"agent_results": [result]}

    async def social_node(state: AnalysisState) -> dict:
        result = await social.run(state["ticker"])
        return {"agent_results": [result]}

    async def news_node(state: AnalysisState) -> dict:
        result = await news.run(state["ticker"])
        return {"agent_results": [result]}

    def supervisor_node(state: AnalysisState) -> dict:
        result = supervisor.synthesize(state["ticker"], state["agent_results"])
        return {"supervisor": result}

    # Creates a LangGraph where the shared data follows the AnalysisState structure
    graph = StateGraph(AnalysisState)
    graph.add_node("fundamentals", fundamentals_node)
    graph.add_node("social_media", social_node)
    graph.add_node("news", news_node)
    graph.add_node("supervisor", supervisor_node)

    # conditional routing based on if the user selected specific agents
    def router(state: AnalysisState) -> list[str]:
        enabled = state.get("enabled_agents") or list(AgentName)
        return [a.value for a in enabled]

    graph.add_conditional_edges(START, router, ["fundamentals", "social_media", "news"])
    # all agents point to the supervisor agent. adds an edge between all data agents to 
    # supervisor agent. after each agent finishes, the workflow goes to the supervisor
    graph.add_edge("fundamentals", "supervisor")
    graph.add_edge("social_media", "supervisor")
    graph.add_edge("news", "supervisor")
    graph.add_edge("supervisor", END)
    return graph.compile()


_compiled_graph = None


def _get_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = _build_graph()
    return _compiled_graph


# This is the function that gets called by the API endpoint. Crfeates the starting 
# state for the workflow and returns the results in a JSON format
async def run_analysis(
    ticker: str,
    enabled_agents: list[AgentName] | None = None,
) -> AnalysisResponse:
    started = datetime.utcnow()
    initial: AnalysisState = {
        "ticker": ticker,
        "enabled_agents": enabled_agents or list(AgentName),
        "agent_results": [],
    }
    # workflow actually executes. starts from START, routes to the enabled agents, 
    # runs them, sends their results to the supervisor, and returns the final state.
    final_state = await _get_graph().ainvoke(initial)
    completed = datetime.utcnow()
    #returns clean API Response. 
    return AnalysisResponse(
        ticker=ticker,
        started_at=started,
        completed_at=completed,
        agent_results=final_state["agent_results"],
        supervisor=final_state["supervisor"],
    )
