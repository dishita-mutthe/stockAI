# StockAI — Multi-Agent Sentiment Platform

A personal multi-agent AI platform that aggregates and analyzes sentiment from
multiple data sources related to publicly traded stocks. Three specialized
agents (Fundamentals, Social Media, News) collect data independently; a
Supervisor agent synthesizes their outputs into a single Buy / Hold / Sell
signal with reasoning. Results are surfaced through a React dashboard.

See [StockAI_BRD.docx](./StockAI_BRD.docx) for the full Business Requirements
Document.

## Architecture

```
┌──────────────┐    ┌────────────────────────────────────────────┐
│ React + Vite │ ─► │ FastAPI                                    │
│  dashboard   │    │   └─ LangGraph workflow                    │
└──────────────┘    │        ├─ Fundamentals Agent  (FMP)        │
                    │        ├─ Social Media Agent (Reddit/PRAW) │
                    │        ├─ News Agent         (NewsData.io) │
                    │        └─ Supervisor Agent   (Claude)      │
                    │   └─ SQLite                                │
                    └────────────────────────────────────────────┘
```

## Tech Stack

| Layer        | Choice                                       |
|--------------|----------------------------------------------|
| Frontend     | React + Vite + TypeScript + Tailwind CSS     |
| Backend      | Python 3.11+, FastAPI, Uvicorn               |
| Agents       | LangGraph for orchestration & state          |
| LLM          | Anthropic Claude (`claude-sonnet-4-20250514`)|
| Storage      | SQLite (local file)                          |
| Data sources | Financial Modeling Prep, Reddit, NewsData.io |

## Repository Layout

```
stockAI/
├── backend/         FastAPI app, agents, LangGraph workflow
├── frontend/        React + Vite + Tailwind dashboard
├── docs/            Architecture notes, design decisions
└── StockAI_BRD.docx Business Requirements Document
```

## Getting Started

### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in API keys
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

The frontend dev server proxies `/api` calls to `http://localhost:8000`.

## Disclaimer

Outputs from StockAI are **not financial advice**. The system is a personal
research project; verify all data and reasoning independently before making
investment decisions.
