# Architecture

> Companion notes to [StockAI_BRD.docx](../StockAI_BRD.docx). The BRD is the
> source of truth for *what*; this doc explains *how* the scaffold expresses it.

## Request flow

```
React UI
   │  POST /api/analyze { ticker, agents }
   ▼
FastAPI route (app/api/routes/analysis.py)
   │
   ▼
LangGraph workflow (app/graph/workflow.py)
   │
   ├── FundamentalsAgent  ──┐
   ├── SocialMediaAgent  ──┼──►  SupervisorAgent  ──►  AnalysisResponse
   └── NewsAgent         ──┘
```

The three data agents run in parallel through LangGraph's conditional fan-out
from `START`. Each writes a single `AgentResult` into the shared
`agent_results` list (annotated with `operator.add` so concurrent updates
merge instead of clobbering). When all selected agents finish, the
`supervisor` node runs and writes the final `SupervisorResult`.

## Agent contract

Every data agent extends `BaseAgent` and implements two hooks:

| Method          | Purpose                                                 |
|-----------------|---------------------------------------------------------|
| `collect`       | Fetch raw payload from the external API.                |
| `build_prompt`  | Render the (system, user) prompt for the LLM.           |

`BaseAgent.run` handles LLM invocation, JSON parsing, error capture, and
timing. Agents never raise — failures become a neutral `AgentResult` with the
error surfaced so the Supervisor can still produce a signal.

## Guardrails (BRD §8)

- Prompts forbid invented metrics; the LLM is told to use only the provided data.
- API keys live in env vars, loaded once by `app.config.Settings`.
- Every `AnalysisResponse` carries a "not financial advice" disclaimer.
- All agent inputs, outputs, and runtimes are logged (`app.utils.logging`).

## Adding a v2 agent

1. Add a new value to `AgentName` in [app/models/schemas.py](../backend/app/models/schemas.py).
2. Create `app/agents/<name>_agent.py` subclassing `BaseAgent`.
3. Add the corresponding prompt module under `app/prompts/`.
4. Register a node + edge in [app/graph/workflow.py](../backend/app/graph/workflow.py).
5. Add the agent option to `AgentSelector` in the frontend.
