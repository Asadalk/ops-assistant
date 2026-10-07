# Resume Claim Verification

Verified: 2026-10-07

## Claim 1

**CLAIM**

Full-stack AI operations assistant from Next.js through FastAPI, Gemini, and SQLite.

**IMPLEMENTATION**

The Next.js form calls `/extract`; FastAPI retrieves operational context, calls Gemini, validates the structured response with Pydantic, persists tasks in SQLite, and returns them to the Kanban board.

**FILES**

`frontend/app/page.tsx`, `frontend/lib/api.ts`, `backend/routes/tasks.py`, `backend/services/rag.py`, `backend/services/gemini.py`, `backend/services/task_service.py`, `backend/database.py`

**TEST**

Live HTTP extraction and browser flow from the input form to the Kanban board, including status persistence and deletion after reload.

**RESULT**

PASS

## Claim 2

**CLAIM**

FastAPI REST APIs integrate the frontend, LLM, and persistent task backend.

**IMPLEMENTATION**

FastAPI exposes health, extraction, task listing, status update, and deletion endpoints with Pydantic models, CORS, SQLite persistence, and controlled HTTP errors.

**FILES**

`backend/main.py`, `backend/routes/tasks.py`, `backend/models.py`, `backend/services/task_service.py`

**TEST**

`backend/.venv311/bin/python -m pytest -q` plus live checks for health, extraction, CRUD, invalid input, and missing task IDs.

**RESULT**

PASS

## Claim 3

**CLAIM**

Gemini structured output, validation, retry, and failure handling.

**IMPLEMENTATION**

The Google GenAI SDK requests JSON matching a task schema. The complete response is validated with Pydantic before SQLite writes. Malformed responses retry once; upstream failures try preferred fallback models and return controlled 502/504 errors.

**FILES**

`backend/services/gemini.py`, `backend/models.py`, `backend/tests/test_gemini.py`, `backend/tests/test_tasks.py`

**TEST**

Tests cover valid output, malformed output followed by a valid retry, repeated invalid output, timeout classification, missing keys, and fallback attempts. Real Gemini extraction succeeded locally and through Docker.

**RESULT**

PASS

## Claim 4

**CLAIM**

Lightweight RAG over operational guidelines provides context during inference.

**IMPLEMENTATION**

Guideline paragraphs are loaded as source-attributed chunks, normalized and scored with IDF-weighted lexical overlap, and the top relevant chunks are inserted into the Gemini prompt before generation.

**FILES**

`backend/services/rag.py`, `backend/guidelines/operational-guidelines.md`, `backend/routes/tasks.py`, `backend/services/gemini.py`, `backend/tests/test_rag.py`, `backend/tests/test_gemini.py`

**TEST**

RAG tests cover production outages, security exposure, deployment verification, irrelevant queries, source metadata, and prompt-context wiring.

**RESULT**

PASS

## Claim 5

**CLAIM**

Docker Compose supports reproducible frontend and backend execution.

**IMPLEMENTATION**

Separate Dockerfiles build the Python backend and Next.js production frontend. Compose starts both services and gates frontend startup on the backend healthcheck.

**FILES**

`docker-compose.yml`, `backend/Dockerfile`, `frontend/Dockerfile`

**TEST**

`docker compose build` passed. `docker compose up` started both services; health, frontend reachability, real Gemini extraction, PATCH, and DELETE passed. One transient upstream timeout returned a controlled 502 before a subsequent real request succeeded.

**RESULT**

PASS

## Limitations

This is a single-user portfolio MVP without authentication or a persistent Docker volume. The guideline file is illustrative demo context and must be reviewed before real organizational use. Gemini can still make semantic extraction mistakes. The browser never receives the Gemini API key.
