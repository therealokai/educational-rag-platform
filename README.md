
# Educational RAG Platform  Quick start

This project provides a small FastAPI service that generates validated multiple-choice questions (MCQs) from a query + relevant context (retrieved from a vector store). The service uses an LLM to generate candidate questions and an evaluator agent to validate them until the requested number of valid questions is reached (or a maximum iteration cap).

## Requirements
- Docker & Docker Compose 
- Python 3.10+ (if you prefer to run locally without Docker)

## Required environment variables
Copy `.env.example` to `.env` and fill in the values:

- `OPENAI_API_KEY` (required)  your OpenAI API key (or other key used by the configured LLM provider)
- `QDRANT_URL` (optional)  URL to Qdrant (default `http://localhost:6333`)
- `QDRANT_API_KEY` (optional)  if you use a hosted Qdrant with an API key
- `TEMPERATURE` (optional)  LLM temperature (defaults in config)
- `MAX_ITERATIONS` (optional)  safety cap for generator/evaluator loop

Example:

```
cp .env.example .env
# edit .env and set OPENAI_API_KEY
```

## Run with Docker 

The project has a `docker-compose.yml` that starts a Qdrant vector DB and the app.

1. Build and run:

```bash
docker compose up --build
```

2. The API will be available at http://localhost:8000. OpenAPI docs at:

- `http://localhost:8000/api/v1/openapi.json`
- `http://localhost:8000/docs`  For FastAPI Swagger
- `http://localhost:6333/dashboard` For Qdrant Dashboard

## Run locally without Docker

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Ensure you have Qdrant running (or change `QDRANT_URL` to your vector store). Then run the app:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API: Generate questions

POST /api/v1/generate/questions/

Request body (JSON):

```json
{
	"query": "Explain the process of photosynthesis",
	"num_questions": 5
}
```

Notes:
- `query` must be present and less than 250 characters, otherwise the API returns HTTP 400.
- `num_questions` is optional (defaults to 5 in the schema) and requests how many valid MCQs you want.


Example response:

```json
{
	"questions": [
		"What organelle is the site of photosynthesis? A) Mitochondria B) Chloroplast C) Nucleus D) Ribosome Answer: B",
		"Which pigment absorbs light for photosynthesis? A) Hemoglobin B) Chlorophyll C) Melanin D) Carotene Answer: B"
	],
	"evaluation": "Evaluator summary...",
	"iterations": 2,
	"passed": true
}
```

If the service cannot reach the requested number of valid questions within the iteration cap, it returns whatever valid questions it accumulated and `passed` may be false.

## Ingesting content for the RAG vector store

There is an ingest endpoint in the API (`/api/v1/ingest`) used to add documents into the vector store (Qdrant). Run that first with your documents or use the `app/services/ingest_service.py` helper to programmatically add content. The question generator retrieves context from the vector store before generating questions.

