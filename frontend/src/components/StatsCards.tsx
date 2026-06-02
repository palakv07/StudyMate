type Stats = {
  solved_count?: number;
  total_problems?: number;
  topic_distribution?: Record<string, number>;
  weak_topics?: { topic: string; avg_weakness: number }[];
  average_solve_time?: number;
  sheet_name?: string;
  sheet_url?: string;
};

export default function StatsCards({
  stats,
  totalFromList = 0,
}: {
  stats: Stats | null;
  totalFromList?: number;
}) {
  if (!stats) {
    return (
      <div className="grid gap-4 sm:grid-cols-3">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="h-24 animate-pulse rounded-2xl bg-slate-800"
          />
        ))}
      </div>
    );
  }

  const solved = stats.solved_count ?? 0;
  const total = stats.total_problems ?? totalFromList ?? 0;
  const topicDist = stats.topic_distribution ?? {};
  const topTopic = Object.entries(topicDist).sort((a, b) => b[1] - a[1])[0];

  return (
    <div className="space-y-3">
      <div className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-2xl border border-slate-700 bg-gradient-to-br from-brand-700/40 to-slate-900 p-5">
          <p className="text-sm text-slate-400">Solved</p>
          <p className="text-3xl font-bold text-white">{solved}</p>
          <p className="mt-1 text-xs text-slate-500">of {total} in sheet</p>
        </div>
        <div className="rounded-2xl border border-slate-700 bg-slate-900/80 p-5">
          <p className="text-sm text-slate-400">Total problems</p>
          <p className="text-3xl font-bold text-white">{total}</p>
        </div>
        <div className="rounded-2xl border border-slate-700 bg-slate-900/80 p-5">
          <p className="text-sm text-slate-400">Top topic</p>
          <p className="text-xl font-bold text-white">
            {topTopic ? topTopic[0] : "—"}
          </p>
        </div>
      </div>
      {stats.sheet_url ? (
        <p className="text-xs text-slate-500">
          Reading Google Sheet:{" "}
          <a
            href={stats.sheet_url}
            target="_blank"
            rel="noreferrer"
            className="text-brand-500 underline"
          >
            {stats.sheet_name || "Open sheet"}
          </a>
          {" — "}
          edit this file in Google Sheets (not Excel desktop).
        </p>
      ) : total > 0 && solved === 0 ? (
        <p className="text-xs text-amber-400/90">
          Data loaded but 0 solved — restart backend (backend/start_backend.bat) so
          &quot;Accepted&quot; status is recognized. Status column must be Accepted or
          Solved.
        </p>
      ) : null}
    </div>
  );
}
