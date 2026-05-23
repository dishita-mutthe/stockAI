interface Props {
  ticker: string;
  onChange: (next: string) => void;
  disabled?: boolean;
}

export function StockSelector({ ticker, onChange, disabled }: Props) {
  return (
    <label className="block">
      <span className="block text-sm font-medium text-slate-700">Ticker</span>
      <input
        type="text"
        value={ticker}
        onChange={(e) => onChange(e.target.value.toUpperCase())}
        disabled={disabled}
        placeholder="AAPL"
        maxLength={10}
        className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 uppercase shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 disabled:bg-slate-100"
      />
    </label>
  );
}
