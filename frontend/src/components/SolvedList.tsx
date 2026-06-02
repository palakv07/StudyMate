import type { Problem } from "../api/client";
import { isProblemSolved } from "../utils/problemStatus";

export default function SolvedList({ problems }: { problems: Problem[] }) {
  const solved = problems.filter(isProblemSolved);

  return (
    <section className="rounded-2xl border border-slate-700 bg-slate-900/80 p-6">
      <h2 className="mb-4 text-lg font-semibold">
        Solved Questions ({solved.length})
      </h2>
      {solved.length === 0 ? (
        <p className="text-sm text-slate-500">
          No solved problems yet. Status must be &quot;Solved&quot; or &quot;Accepted&quot; in
          Google Sheets.
        </p>
      ) : (
        <div className="max-h-64 overflow-y-auto">
          <table className="w-full text-left text-sm">
            <thead className="text-slate-500">
              <tr>
                <th className="pb-2">Problem</th>
                <th className="pb-2">Topic</th>
                <th className="pb-2">Status</th>
                <th className="pb-2">Time</th>
              </tr>
            </thead>
            <tbody>
              {solved.map((p) => (
                <tr key={p.problem} className="border-t border-slate-800">
                  <td className="py-2 font-medium text-white">{p.problem}</td>
                  <td className="py-2 text-slate-400">{p.topic}</td>
                  <td className="py-2 text-slate-400">{p.status}</td>
                  <td className="py-2 text-slate-400">{p.time_taken || "—"}m</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
