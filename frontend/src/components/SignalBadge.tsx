import type { FinalSignal, Signal } from "../types/analysis";

type AnySignal = Signal | FinalSignal;

const COLORS: Record<AnySignal, string> = {
  // Per-agent
  bullish: "bg-emerald-100 text-emerald-800 ring-emerald-600/20",
  bearish: "bg-rose-100 text-rose-800 ring-rose-600/20",
  neutral: "bg-slate-100 text-slate-700 ring-slate-500/20",
  // Supervisor
  buy: "bg-emerald-100 text-emerald-800 ring-emerald-600/20",
  buy_with_caution: "bg-amber-100 text-amber-800 ring-amber-600/20",
  hold: "bg-slate-100 text-slate-700 ring-slate-500/20",
  sell_with_caution: "bg-orange-100 text-orange-800 ring-orange-600/20",
  sell: "bg-rose-100 text-rose-800 ring-rose-600/20",
};

interface Props {
  signal: AnySignal;
  size?: "sm" | "lg";
}

export function SignalBadge({ signal, size = "sm" }: Props) {
  const sizing = size === "lg" ? "px-4 py-2 text-base" : "px-2 py-0.5 text-xs";
  return (
    <span
      className={`inline-flex items-center rounded-full font-medium ring-1 ring-inset ${COLORS[signal]} ${sizing}`}
    >
      {signal.replace(/_/g, " ").toUpperCase()}
    </span>
  );
}
