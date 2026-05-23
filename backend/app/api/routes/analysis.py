"""POST /api/analyze — run the multi-agent workflow for a single ticker."""

from fastapi import APIRouter, HTTPException

from app.graph.workflow import run_analysis
from app.models.schemas import AnalysisRequest, AnalysisResponse

router = APIRouter(tags=["analysis"])


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze(request: AnalysisRequest) -> AnalysisResponse:
    """Run the selected agents and return the Supervisor's synthesized signal.

    Per BRD §7 / §8, this is the single user-facing entrypoint in v1 and should
    complete within 60-90s for one ticker.
    """
    try:
        return await run_analysis(
            ticker=request.ticker.upper(),
            enabled_agents=request.agents,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
