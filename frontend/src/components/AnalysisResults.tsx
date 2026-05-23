import type { AnalysisResponse } from "../types/analysis";
import { AgentResultPanel } from "./AgentResultPanel";
import { SignalBadge } from "./SignalBadge";

interface Props {
  result: AnalysisResponse;
}

export function AnalysisResults({ result }: Props) {
  const { supervisor, agent_results, completed_at, disclaimer } = result;

  return (
    <section className="space-y-4">
      <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-semibold">{supervisor.ticker}</h2>
          <SignalBadge signal={supervisor.final_signal} size="lg" />
        </div>
        <p className="mt-3 text-sm text-slate-700">{supervisor.rationale}</p>

        {supervisor.conflicts.length > 0 && (
          <div className="mt-4 rounded-md bg-amber-50 p-3 text-sm text-amber-800">
            <p className="font-medium">Conflicts detected</p>
            <ul className="ml-5 list-disc">
              {supervisor.conflicts.map((c) => (
                <li key={c}>{c}</li>
              ))}
            </ul>
          </div>
        )}

        <p className="mt-4 text-xs text-slate-500">
          Last run: {new Date(completed_at).toLocaleString()}
        </p>
      </div>

      <div className="space-y-2">
        {agent_results.map((r) => (
          <AgentResultPanel key={r.agent} result={r} />
        ))}
      </div>

      <p className="text-xs italic text-slate-500">{disclaimer}</p>
    </section>
  );
}
