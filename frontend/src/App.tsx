import { useCallback, useEffect, useState } from "react";
import {
  checkBackendHealth,
  fetchProblems,
  fetchRecommendations,
  fetchStats,
  type Problem,
} from "./api/client";
import SolveForm from "./components/SolveForm";
import StatsCards from "./components/StatsCards";
import WeakTopics from "./components/WeakTopics";
import Recommendations from "./components/Recommendations";
import SolvedList from "./components/SolvedList";
import { countSolved } from "./utils/problemStatus";

export default function App() {
  const [stats, setStats] = useState<Awaited<ReturnType<typeof fetchStats>> | null>(
    null
  );
  const [problems, setProblems] = useState<Problem[]>([]);
  const [recs, setRecs] = useState<{
    recommendations: [];
    ai_advice: string;
    weak_topics: { topic: string; avg_weakness: number }[];
  } | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [recError, setRecError] = useState<string | null>(null);
  const [backendUp, setBackendUp] = useState<boolean | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    try {
      setLoadError(null);
      setRecError(null);
      setLoading(true);
      const healthy = await checkBackendHealth();
      setBackendUp(healthy);
      if (!healthy) {
        setLoadError(
          "Unable to connect to the backend service. Please wait a few seconds and refresh the page."
        );
        return;
      }
      const [s, p] = await Promise.all([fetchStats(), fetchProblems()]);
      const solvedFromList = countSolved(p);
      setStats({
        ...s,
        solved_count:
          (s.solved_count ?? 0) > 0 ? s.solved_count : solvedFromList,
        total_problems: s.total_problems ?? p.length,
      });
      setProblems(p);

      try {
        const r = await fetchRecommendations();
        setRecs(r);
      } catch (e) {
        setRecs({
          recommendations: [],
          ai_advice: "",
          weak_topics: s?.weak_topics || [],
        });
        setRecError(
          e instanceof Error ? e.message : "Failed to load recommendations"
        );
      }
    } catch (e) {
      setLoadError(
        e instanceof Error
          ? e.message
          : "Could not reach backend.check backend/.env"
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return (
    <div className="min-h-screen bg-slate-950">
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-5">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white">
              AI StudyMate
            </h1>
            <p className="text-sm text-slate-400">
              LeetCode coach · Sheets · Notion · Coral SQL · Gemini
            </p>
          </div>
          <button
            type="button"
            onClick={refresh}
            className="rounded-lg border border-slate-600 px-4 py-2 text-sm hover:bg-slate-800"
          >
            Refresh
          </button>
        </div>
      </header>

      <main className="mx-auto max-w-6xl space-y-6 px-4 py-8">
        {backendUp === false && (
          <div className="rounded-lg border border-amber-700 bg-amber-950/40 p-4 text-sm text-amber-200">
            <p className="font-medium">Backend offline</p>
            <p className="mt-1">{loadError}</p>
            <p className="mt-2 text-xs text-amber-400/80">
              Test in browser:{" "}
              <a className="underline" href="https://studymate-c8y7.onrender.com/health">
                https://studymate-c8y7.onrender.com/health
              </a>{" "}
              should show {`{"status":"ok"}`}
            </p>
          </div>
        )}
        {loadError && backendUp !== false && (
          <div className="rounded-lg border border-red-800 bg-red-950/50 p-4 text-sm text-red-300">
            {loadError}
          </div>
        )}

        {recError && (
          <div className="rounded-lg border border-amber-800 bg-amber-950/40 p-4 text-sm text-amber-200">
            Recommendations: {recError}
          </div>
        )}

        {loading && !stats && (
          <p className="text-sm text-slate-500">Loading your sheet data…</p>
        )}

        <StatsCards stats={stats} totalFromList={problems.length} />

        <div className="grid gap-6 lg:grid-cols-2">
          <SolveForm onSuccess={refresh} />
          <WeakTopics topics={recs?.weak_topics || stats?.weak_topics || []} />
        </div>

        <Recommendations
          recommendations={recs?.recommendations || []}
          aiAdvice={recs?.ai_advice || ""}
        />

        <SolvedList problems={problems} />
      </main>
    </div>
  );
}
