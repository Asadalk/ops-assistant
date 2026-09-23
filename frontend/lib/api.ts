import type { ExtractPayload, Task, UpdateTaskPayload } from "@/types/task";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const DEFAULT_API_TIMEOUT_MS = 30000;

function getApiTimeoutMs(): number {
  const parsed = Number(process.env.NEXT_PUBLIC_API_TIMEOUT_MS);
  if (!Number.isFinite(parsed) || parsed <= 0) {
    return DEFAULT_API_TIMEOUT_MS;
  }
  return Math.floor(parsed);
}

const API_TIMEOUT_MS = getApiTimeoutMs();

async function fetchWithTimeout(input: string, init?: RequestInit): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT_MS);

  try {
    return await fetch(input, {
      ...init,
      signal: controller.signal,
    });
  } catch (error: unknown) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new Error(
        `Request timed out after ${Math.round(API_TIMEOUT_MS / 1000)}s. Check backend logs or try again.`,
      );
    }
    throw error;
  } finally {
    clearTimeout(timeoutId);
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let message = `Request failed (${res.status})`;
    try {
      const data: unknown = await res.json();
      if (typeof data === "object" && data !== null && "detail" in data) {
        const detail = (data as { detail?: unknown }).detail;
        if (typeof detail === "string") {
          message = detail;
        }
      }
    } catch {
      // Keep the status-based message when the server did not return JSON.
    }
    throw new Error(message);
  }

  return (await res.json()) as T;
}

export async function extractTasks(payload: ExtractPayload): Promise<Task[]> {
  const res = await fetchWithTimeout(`${API_BASE_URL}/extract`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  return handleResponse<Task[]>(res);
}

export async function fetchTasks(): Promise<Task[]> {
  const res = await fetchWithTimeout(`${API_BASE_URL}/tasks`, {
    cache: "no-store",
  });
  return handleResponse<Task[]>(res);
}

export async function patchTask(id: number, payload: UpdateTaskPayload): Promise<Task> {
  const res = await fetchWithTimeout(`${API_BASE_URL}/tasks/${id}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  return handleResponse<Task>(res);
}

export async function deleteTask(id: number): Promise<void> {
  const res = await fetchWithTimeout(`${API_BASE_URL}/tasks/${id}`, {
    method: "DELETE",
  });
  await handleResponse<{ message: string }>(res);
}
