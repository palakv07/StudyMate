import { useEffect, useState } from "react";
import { getCalendarAuthUrl, getCalendarStatus, scheduleCalendar } from "../api/client";

export default function CalendarControls({ recommendations }: { recommendations: any[] }) {
  const [connected, setConnected] = useState<boolean | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function check() {
      try {
        const s = await getCalendarStatus();
        setConnected(Boolean(s.connected));
      } catch {
        setConnected(false);
      }
    }
    check();
  }, []);

  const connect = async () => {
    try {
      const { url } = await getCalendarAuthUrl();
      // open auth URL in new tab; callback will persist token server-side
      window.open(url, "_blank");
      alert("A new tab opened for Google Calendar authorization. After granting access, return here and click 'Refresh status'.");
    } catch (e: any) {
      alert(e.message || "Failed to start auth");
    }
  };

  const refresh = async () => {
    try {
      const s = await getCalendarStatus();
      setConnected(Boolean(s.connected));
      if (s.connected) alert("Calendar connected");
    } catch (e: any) {
      alert(e.message || "Failed to fetch status");
    }
  };

  const schedule = async () => {
    if (!recommendations || recommendations.length === 0) {
      alert("No recommendations to schedule");
      return;
    }
    setLoading(true);
    try {
      // convert recommendations to items with title + duration
      const items = recommendations.map((r: any) => ({ title: r.problem, duration_mins: 60 }));
      await scheduleCalendar(items);
      alert("Scheduled recommendations to your calendar.");
    } catch (e: any) {
      alert(e.message || "Failed to schedule");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mt-4 flex items-center gap-3">
      {connected ? (
        <>
          <button onClick={schedule} className="btn btn-primary" disabled={loading}>
            {loading ? "Scheduling…" : "Schedule to Calendar"}
          </button>
          <button onClick={refresh} className="btn">
            Refresh status
          </button>
        </>
      ) : (
        <>
          <button onClick={connect} className="btn btn-secondary">
            Connect Google Calendar
          </button>
          <button onClick={refresh} className="btn">
            Refresh status
          </button>
        </>
      )}
    </div>
  );
}
