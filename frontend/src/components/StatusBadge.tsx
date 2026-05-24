import type { AgentStatus } from "../types/analysis";

// Lighter/flatter than SignalBadge on purpose — status sits next to the signal
// in the panel header and shouldn't compete for attention.
const COLORS: Record<AgentStatus, string> = {
  success: "bg-emerald-50 text-emerald-700 ring-emerald-600/20",
  partial: "bg-amber-50 text-amber-800 ring-amber-600/20",
  error: "bg-rose-50 text-rose-700 ring-rose-600/20",
};

const LABELS: Record<AgentStatus, string> = {
  success: "OK",
  partial: "Partial",
  error: "Error",
};

interface Props {
  status: AgentStatus;
}

export function StatusBadge({ status }: Props) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ring-1 ring-inset ${COLORS[status]}`}
      title={`Agent status: ${status}`}
    >
      {LABELS[status]}
    </span>
  );
}
