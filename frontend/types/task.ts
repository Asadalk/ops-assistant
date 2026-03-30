export type Priority = "high" | "medium" | "low";
export type TaskStatus = "todo" | "in_progress" | "done";

export interface Task {
  id: number;
  task: string;
  owner: string;
  deadline: string;
  priority: Priority;
  status: TaskStatus;
  created_at: string;
}

export interface ExtractPayload {
  text: string;
}

export interface UpdateTaskPayload {
  status: TaskStatus;
}
