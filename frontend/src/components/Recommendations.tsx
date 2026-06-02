type Rec = {
  problem: string;
  topic: string;
  difficulty: string;
  weakness_score: number;
};
import CalendarControls from "./CalendarControls";

export default function Recommendations({
  recommendations,
  aiAdvice,
}: {
  recommendations: Rec[];
  aiAdvice: string;
}) {
  return (
  <section className="rounded-2xl border border-slate-700 bg-slate-900/80 p-6">
    <h2 className="mb-2 text-lg font-semibold">AI Recommendations</h2>

    <p className="mb-4 rounded-lg bg-brand-600/20 p-4 text-sm leading-relaxed text-slate-200">
      {aiAdvice || "Loading advice…"}
    </p>

    {typeof window !== "undefined" ? (
      <CalendarControls recommendations={recommendations} />
    ) : null}

    <ol className="list-decimal space-y-2 pl-5 text-sm text-slate-300">
      {recommendations.map((r) => (
        <li key={r.problem}>
          <span className="font-medium text-white">{r.problem}</span>
          <span className="text-slate-500">
            {" "}
            — {r.topic}, {r.difficulty} (priority {r.weakness_score})
          </span>
        </li>
      ))}
    </ol>
  </section>
);
}
