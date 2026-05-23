import { useState } from "react";
import type { AgentResult } from "../types/analysis";
import { SignalBadge } from "./SignalBadge";

const AGENT_LABELS: Record<AgentResult["agent"], string> = {
  fundamentals: "Fundamentals",
  social_media: "Social Media",
  news: "News",
};

interface Props {
  result: AgentResult;
}

export function AgentResultPanel({ result }: Props) {
  const [open, setOpen] = useState(false);

  return (
    <div className="rounded-lg border border-slate-200 bg-white">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between px-4 py-3 text-left"
      >
        <span className="flex items-center gap-3">
          <span className="font-medium">{AGENT_LABELS[result.agent]}</span>
          <SignalBadge signal={result.signal} />
        </span>
        <span className="text-sm text-slate-500">{open ? "Hide" : "Show"} details</span>
      </button>

      {open && (
        <div className="space-y-3 border-t border-slate-200 px-4 py-3">
          <p className="text-sm text-slate-700">{result.summary}</p>
          {result.error && (
            <p className="text-sm text-rose-600">Error: {result.error}</p>
          )}
          <details className="text-xs text-slate-500">
            <summary className="cursor-pointer">Raw data</summary>
            <pre className="mt-2 max-h-64 overflow-auto rounded bg-slate-50 p-2">
              {JSON.stringify(result.data, null, 2)}
            </pre>
          </details>
        </div>
      )}
    </div>
  );
}
