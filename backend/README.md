# StockAI Backend

FastAPI app exposing a single analysis endpoint that runs a LangGraph workflow
over three data agents plus a Supervisor.

## Layout

```
app/
├── main.py            FastAPI entrypoint + CORS
├── config.py          Settings loaded from env / .env
├── db.py              SQLite engine + session
├── api/routes/        REST endpoints
├── agents/            Fundamentals / SocialMedia / News / Supervisor
├── graph/             LangGraph state + workflow wiring
├── clients/           Thin wrappers around FMP, Reddit, NewsData, Claude
├── models/            Pydantic schemas + SQLAlchemy ORM
├── prompts/           Prompt templates per agent
└── utils/             Logging, helpers
```

## Run locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in keys
uvicorn app.main:app --reload --port 8000
```

Visit `http://localhost:8000/docs` for the OpenAPI UI.

## Tests

```bash
pytest
```
