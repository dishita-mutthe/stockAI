import type { AnalysisRequest, AnalysisResponse } from "../types/analysis";

export async function runAnalysis(req: AnalysisRequest): Promise<AnalysisResponse> {
  const resp = await fetch("/api/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!resp.ok) {
    const detail = await resp.text();
    throw new Error(`Analysis failed (${resp.status}): ${detail}`);
  }
  return (await resp.json()) as AnalysisResponse;
}
