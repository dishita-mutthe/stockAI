import { useState } from "react";
import { runAnalysis } from "./api/client";
import { AgentSelector } from "./components/AgentSelector";
import { AnalysisResults } from "./components/AnalysisResults";
import { StockSelector } from "./components/StockSelector";
import type { AgentName, AnalysisResponse } from "./types/analysis";

const DEFAULT_AGENTS: AgentName[] = ["fundamentals", "social_media", "news"];

export default function App() {
  const [ticker, setTicker] = useState("");
  const [agents, setAgents] = useState<AgentName[]>(DEFAULT_AGENTS);
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const start = async () => {
    if (!ticker.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const next = await runAnalysis({ ticker: ticker.trim(), agents });
      setResult(next);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="mx-auto max-w-3xl px-4 py-10">
      <header className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">StockAI</h1>
        <p className="mt-1 text-sm text-slate-600">
          Multi-agent sentiment analysis for a single ticker.
        </p>
      </header>

      <section className="mb-8 grid grid-cols-1 gap-6 rounded-lg border border-slate-200 bg-white p-6 shadow-sm md:grid-cols-2">
        <StockSelector ticker={ticker} onChange={setTicker} disabled={loading} />
        <AgentSelector selected={agents} onChange={setAgents} disabled={loading} />
        <div className="md:col-span-2">
          <button
            type="button"
            onClick={start}
            disabled={loading || !ticker.trim() || agents.length === 0}
            className="inline-flex items-center rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 disabled:cursor-not-allowed disabled:bg-slate-300"
          >
            {loading ? "Analyzing…" : "Start Analysis"}
          </button>
        </div>
      </section>

      {error && (
        <div className="mb-6 rounded-md bg-rose-50 p-3 text-sm text-rose-800">{error}</div>
      )}

      {loading && (
        <div className="mb-6 rounded-md bg-slate-100 p-3 text-sm text-slate-700">
          Agents are working — this usually takes 60–90 seconds.
        </div>
      )}

      {result && <AnalysisResults result={result} />}
    </main>
  );
}
