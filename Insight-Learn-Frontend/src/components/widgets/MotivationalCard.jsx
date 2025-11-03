import { useQuery } from "@tanstack/react-query";
import { getMotivationToday } from "../../api/motivation";
import { RefreshCw, Copy } from "lucide-react";
import { useState } from "react";

export default function MotivationCard() {
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState(null);

  const { data: quote } = useQuery({
    queryKey: ["motivation", "today"],
    queryFn: async () => {
      try {
        setError(null);
        return await getMotivationToday();
      } catch (e) {
        console.error("Failed to fetch motivation quote:", e);
        setError("Unable to load today’s quote. Please try again.");
        throw e; // keep react-query aware of the error
      }
    },
    staleTime: 1000 * 60 * 30, // 30 minutes
    retry: 1,
  });

  async function copyText() {
    if (!quote) return;
    try {
      await navigator.clipboard.writeText(`${quote.text} — ${quote.author}`);
      setCopied(true);
      setTimeout(() => setCopied(false), 1200);
    } catch (e) {
      console.error("Clipboard copy failed:", e);
      setError("Copy failed. Please select the text and copy manually.");
    }
  }

  return (
    <div className="card bg-base-100 shadow">
      <div className="card-body gap-3">
        <div className="flex items-center justify-between">
          <h2 className="card-title">Daily Motivation</h2>
        </div>

        {error && (
          <div role="alert" className="alert alert-warning text-sm">
            {error}
          </div>
        )}

        <blockquote className="text-sm leading-relaxed">
          <span className="opacity-90">“{quote?.text ?? "Keep going!"}”</span>
          <div className="mt-2 text-xs opacity-70">— {quote?.author || "Unknown"}</div>
        </blockquote>

        <div className="card-actions justify-end">
          <button className="btn btn-ghost btn-sm" onClick={copyText}>
            <Copy className="h-4 w-4 mr-1" />
            {copied ? "Copied" : "Copy"}
          </button>
        </div>
      </div>
    </div>
  );
}