import { useState } from "react";
import { markSolved, type SolvePayload } from "../api/client";

type Props = { onSuccess: () => void };

const TOPICS = ["Arrays", "DP", "Graph", "Trees", "Stack", "Two Pointers", "Intervals"];
const DIFFICULTIES = ["Easy", "Medium", "Hard"];

export default function SolveForm({ onSuccess }: Props) {
  const [form, setForm] = useState<SolvePayload>({
    problem: "",
    topic: "DP",
    difficulty: "Medium",
    time_taken: 30,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setMessage(null);
    try {
      const result = await markSolved(form);
      setMessage(result.message || "Marked as solved!");
      setForm({ ...form, problem: "", time_taken: 30 });
      onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="rounded-2xl border border-slate-700 bg-slate-900/80 p-6 shadow-xl">
      <h2 className="mb-4 text-lg font-semibold text-white">Mark Solved</h2>
      <form onSubmit={handleSubmit} className="grid gap-4 sm:grid-cols-2">
        <label className="flex flex-col gap-1 sm:col-span-2">
          <span className="text-sm text-slate-400">Problem name</span>
          <input
            required
            className="rounded-lg border border-slate-600 bg-slate-800 px-3 py-2 text-white"
            placeholder="Coin Change"
            value={form.problem}
            onChange={(e) => setForm({ ...form, problem: e.target.value })}
          />
        </label>
        <label className="flex flex-col gap-1">
          <span className="text-sm text-slate-400">Topic</span>
          <select
            className="rounded-lg border border-slate-600 bg-slate-800 px-3 py-2"
            value={form.topic}
            onChange={(e) => setForm({ ...form, topic: e.target.value })}
          >
            {TOPICS.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </label>
        <label className="flex flex-col gap-1">
          <span className="text-sm text-slate-400">Difficulty</span>
          <select
            className="rounded-lg border border-slate-600 bg-slate-800 px-3 py-2"
            value={form.difficulty}
            onChange={(e) => setForm({ ...form, difficulty: e.target.value })}
          >
            {DIFFICULTIES.map((d) => (
              <option key={d} value={d}>
                {d}
              </option>
            ))}
          </select>
        </label>
        <label className="flex flex-col gap-1 sm:col-span-2">
          <span className="text-sm text-slate-400">Time taken (minutes)</span>
          <input
            type="number"
            min={1}
            required
            className="rounded-lg border border-slate-600 bg-slate-800 px-3 py-2"
            value={form.time_taken}
            onChange={(e) =>
              setForm({ ...form, time_taken: parseInt(e.target.value, 10) || 1 })
            }
          />
        </label>
        <button
          type="submit"
          disabled={loading}
          className="sm:col-span-2 rounded-lg bg-brand-600 px-4 py-3 font-medium text-white hover:bg-brand-700 disabled:opacity-50"
        >
          {loading ? "Syncing…" : "Mark Solved"}
        </button>
      </form>
      {error && <p className="mt-3 text-sm text-red-400">{error}</p>}
      {message && <p className="mt-3 text-sm text-emerald-400">{message}</p>}
      <p className="mt-3 text-xs text-slate-500">
        Syncs to Google Sheets, Notion, and Coral CSV automatically.
      </p>
    </section>
  );
}
