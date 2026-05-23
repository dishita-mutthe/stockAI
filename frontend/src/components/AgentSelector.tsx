import type { AgentName } from "../types/analysis";

const ALL_AGENTS: { name: AgentName; label: string }[] = [
  { name: "fundamentals", label: "Fundamentals (FMP)" },
  { name: "social_media", label: "Social Media (Reddit)" },
  { name: "news", label: "News (NewsData.io)" },
];

interface Props {
  selected: AgentName[];
  onChange: (next: AgentName[]) => void;
  disabled?: boolean;
}

export function AgentSelector({ selected, onChange, disabled }: Props) {
  const toggle = (name: AgentName) => {
    onChange(selected.includes(name) ? selected.filter((n) => n !== name) : [...selected, name]);
  };

  return (
    <fieldset className="space-y-2">
      <legend className="text-sm font-medium text-slate-700">Agents</legend>
      {ALL_AGENTS.map(({ name, label }) => (
        <label key={name} className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={selected.includes(name)}
            onChange={() => toggle(name)}
            disabled={disabled}
            className="h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500"
          />
          <span>{label}</span>
        </label>
      ))}
    </fieldset>
  );
}
