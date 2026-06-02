type WeakTopic = { topic: string; avg_weakness: number };

export default function WeakTopics({ topics }: { topics: WeakTopic[] }) {
  return (
    <section className="rounded-2xl border border-slate-700 bg-slate-900/80 p-6">
      <h2 className="mb-4 text-lg font-semibold">Weak Topics</h2>
      {topics.length === 0 ? (
        <p className="text-sm text-slate-500">Solve a few problems to see weak areas.</p>
      ) : (
        <ul className="space-y-3">
          {topics.map((t) => (
            <li key={t.topic} className="flex items-center justify-between">
              <span className="font-medium text-slate-200">{t.topic}</span>
              <span className="rounded-full bg-amber-500/20 px-3 py-1 text-sm text-amber-300">
                {t.avg_weakness}
              </span>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
