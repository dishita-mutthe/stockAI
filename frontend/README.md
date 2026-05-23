# StockAI Frontend

React + Vite + TypeScript + Tailwind dashboard. Single page, single ticker
analysis in v1 (BRD §7).

## Run

```bash
npm install
npm run dev
```

Dev server runs at `http://localhost:5173` and proxies `/api/*` to the FastAPI
backend at `http://localhost:8000` (see [vite.config.ts](vite.config.ts)).

## Layout

```
src/
├── App.tsx                    Page shell + analyze flow
├── api/client.ts              fetch wrapper for /api/analyze
├── components/
│   ├── StockSelector.tsx
│   ├── AgentSelector.tsx
│   ├── SignalBadge.tsx
│   ├── AgentResultPanel.tsx   collapsible per-agent details
│   └── AnalysisResults.tsx    final signal + agent panels + disclaimer
└── types/analysis.ts          mirrors backend Pydantic models
```
