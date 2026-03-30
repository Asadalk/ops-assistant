import json
import os
from typing import Any

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from database import get_connection, init_db
from models import ExtractRequest, Task, TaskUpdateRequest, normalize_task, now_iso

load_dotenv()

GEMINI_MODEL = "gemini-1.5-flash"
SYSTEM_PROMPT = (
    "You are a task extraction assistant. Extract all action items "
    "from the text. Return ONLY a valid JSON array, no markdown, "
    "no explanation. Format: "
    "[{ task, owner, deadline, priority }] "
    "where priority is 'high', 'medium', or 'low', "
    "owner is 'Unknown' if not mentioned, "
    "deadline is 'Not specified' if not mentioned."
)
RETRY_PROMPT = (
    SYSTEM_PROMPT
    + " IMPORTANT: Output must be strict JSON only, starting with [ and ending with ]."
)

api_key = os.getenv("GEMINI_API_KEY", "").strip()
if api_key:
    genai.configure(api_key=api_key)

RESOLVED_MODEL = GEMINI_MODEL

app = FastAPI(title="Ops Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()

    global RESOLVED_MODEL
    RESOLVED_MODEL = resolve_model_name()


def resolve_model_name() -> str:
    if not api_key:
        return GEMINI_MODEL

    requested_full_name = f"models/{GEMINI_MODEL}"

    try:
        available = {
            model.name
            for model in genai.list_models()
            if "generateContent" in getattr(model, "supported_generation_methods", [])
        }
    except Exception:
        return GEMINI_MODEL

    if requested_full_name in available:
        return GEMINI_MODEL

    preferred_fallbacks = [
        "models/gemini-flash-latest",
        "models/gemini-2.0-flash",
        "models/gemini-2.5-flash",
    ]

    for candidate in preferred_fallbacks:
        if candidate in available:
            return candidate.replace("models/", "")

    for candidate in sorted(available):
        if "flash" in candidate:
            return candidate.replace("models/", "")

    return GEMINI_MODEL


def call_gemini(prompt: str) -> str:
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY is missing in backend/.env")

    model = genai.GenerativeModel(RESOLVED_MODEL)
    try:
        response = model.generate_content(prompt)
    except google_exceptions.GoogleAPIError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Gemini request failed with model '{RESOLVED_MODEL}': {exc}",
        ) from exc
    text = getattr(response, "text", None)

    if not text:
        raise HTTPException(status_code=502, detail="Gemini returned an empty response")

    return text.strip()


def parse_task_array(raw: str) -> list[dict[str, Any]]:
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()

    data = json.loads(cleaned)
    if not isinstance(data, list):
        raise ValueError("Response must be a JSON array")

    result: list[dict[str, Any]] = []
    for item in data:
        if isinstance(item, dict):
            result.append(item)
    return result


def extract_from_text(unstructured_text: str) -> list[dict[str, Any]]:
    primary_prompt = f"{SYSTEM_PROMPT}\n\nTEXT:\n{unstructured_text}"
    first_raw = call_gemini(primary_prompt)

    try:
        return parse_task_array(first_raw)
    except (json.JSONDecodeError, ValueError):
        retry_prompt = f"{RETRY_PROMPT}\n\nTEXT:\n{unstructured_text}"
        retry_raw = call_gemini(retry_prompt)
        try:
            return parse_task_array(retry_raw)
        except (json.JSONDecodeError, ValueError) as exc:
            raise HTTPException(
                status_code=422,
                detail="Could not parse Gemini response as valid task JSON after one retry",
            ) from exc


@app.post("/extract", response_model=list[Task])
def extract_tasks(payload: ExtractRequest) -> list[Task]:
    extracted = extract_from_text(payload.text)

    created: list[Task] = []
    with get_connection() as conn:
        cursor = conn.cursor()

        for raw_item in extracted:
            try:
                normalized = normalize_task(raw_item)
            except ValueError:
                continue

            cursor.execute(
                """
                INSERT INTO tasks (task, owner, deadline, priority, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    normalized.task,
                    normalized.owner,
                    normalized.deadline,
                    normalized.priority,
                    "todo",
                    now_iso(),
                ),
            )
            new_id = cursor.lastrowid

            row = cursor.execute("SELECT * FROM tasks WHERE id = ?", (new_id,)).fetchone()
            if row is not None:
                created.append(Task(**dict(row)))

        conn.commit()

    return created


@app.get("/tasks", response_model=list[Task])
def get_tasks() -> list[Task]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM tasks ORDER BY id DESC").fetchall()
    return [Task(**dict(row)) for row in rows]


@app.patch("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, payload: TaskUpdateRequest) -> Task:
    with get_connection() as conn:
        existing = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if existing is None:
            raise HTTPException(status_code=404, detail="Task not found")

        conn.execute("UPDATE tasks SET status = ? WHERE id = ?", (payload.status, task_id))
        conn.commit()

        updated = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if updated is None:
            raise HTTPException(status_code=500, detail="Task update failed")

    return Task(**dict(updated))


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int) -> dict[str, str]:
    with get_connection() as conn:
        existing = conn.execute("SELECT id FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if existing is None:
            raise HTTPException(status_code=404, detail="Task not found")

        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()

    return {"message": "Task deleted"}
