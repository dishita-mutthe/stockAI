// Mirrors backend/app/models/schemas.py — keep in sync when editing either side.

export type AgentName = "fundamentals" | "social_media" | "news";

export type Signal = "bullish" | "bearish" | "neutral";

export type FinalSignal =
  | "buy"
  | "hold"
  | "sell"
  | "buy_with_caution"
  | "sell_with_caution";

export interface AgentResult {
  agent: AgentName;
  ticker: string;
  signal: Signal;
  summary: string;
  data: Record<string, unknown>;
  error: string | null;
}

export interface SupervisorResult {
  ticker: string;
  final_signal: FinalSignal;
  rationale: string;
  conflicts: string[];
}

export interface AnalysisResponse {
  ticker: string;
  started_at: string;
  completed_at: string;
  agent_results: AgentResult[];
  supervisor: SupervisorResult;
  disclaimer: string;
}

export interface AnalysisRequest {
  ticker: string;
  agents: AgentName[];
}
