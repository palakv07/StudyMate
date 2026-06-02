import type { Problem } from "../api/client";

const SOLVED = new Set([
  "solved",
  "accepted",
  "done",
  "complete",
  "completed",
  "yes",
  "ac",
]);

export function isProblemSolved(p: Problem): boolean {
  const status = String(p.status || "").trim().toLowerCase();
  if (SOLVED.has(status)) return true;
  if (!status && String(p.date_solved || "").trim()) return true;
  const bad = ["wrong", "fail", "timeout", "tle", "mle", "rejected"];
  if (status && bad.some((x) => status.includes(x))) return false;
  return false;
}

export function countSolved(problems: Problem[]): number {
  return problems.filter(isProblemSolved).length;
}
