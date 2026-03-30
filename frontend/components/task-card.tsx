"use client";

import { ChangeEvent } from "react";
import { CalendarDays, Trash2, UserCircle2 } from "lucide-react";

import { Task, TaskStatus } from "@/types/task";

interface TaskCardProps {
  task: Task;
  onStatusChange: (taskId: number, status: TaskStatus) => void;
  onDelete: (taskId: number) => void;
}

const statusOptions: Array<{ label: string; value: TaskStatus }> = [
  { label: "To Do", value: "todo" },
  { label: "In Progress", value: "in_progress" },
  { label: "Done", value: "done" },
];

function priorityBadge(priority: Task["priority"]): string {
  if (priority === "high") {
    return "bg-red-100 text-red-700 border-red-200";
  }
  if (priority === "medium") {
    return "bg-amber-100 text-amber-700 border-amber-200";
  }
  return "bg-emerald-100 text-emerald-700 border-emerald-200";
}

export default function TaskCard({ task, onStatusChange, onDelete }: TaskCardProps) {
  return (
    <article className="rounded-lg border border-slate-200 bg-white p-4 shadow-soft">
      <p className="mb-3 text-sm font-medium leading-6 text-slate-900">{task.task}</p>

      <div className="mb-3 flex items-center gap-2 text-xs text-slate-600">
        <UserCircle2 className="h-4 w-4" />
        <span>{task.owner}</span>
      </div>

      <div className="mb-4 flex items-center gap-2 text-xs text-slate-600">
        <CalendarDays className="h-4 w-4" />
        <span>{task.deadline}</span>
      </div>

      <div className="mb-4 flex items-center justify-between gap-3">
        <span
          className={`rounded-full border px-2.5 py-1 text-xs font-semibold capitalize ${priorityBadge(task.priority)}`}
        >
          {task.priority}
        </span>

        <select
          value={task.status}
          onChange={(event: ChangeEvent<HTMLSelectElement>) =>
            onStatusChange(task.id, event.target.value as TaskStatus)
          }
          className="rounded-md border border-slate-300 bg-white px-2 py-1 text-xs text-slate-700 outline-none focus:border-slate-500"
        >
          {statusOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>

      <button
        type="button"
        onClick={() => onDelete(task.id)}
        className="inline-flex items-center gap-1 rounded-md border border-red-200 px-2 py-1 text-xs font-medium text-red-600 transition hover:bg-red-50"
      >
        <Trash2 className="h-3.5 w-3.5" />
        Delete
      </button>
    </article>
  );
}
