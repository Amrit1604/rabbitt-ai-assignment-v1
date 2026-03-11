import type { UploadStatus } from "@/types";

interface Props {
  status: UploadStatus;
  summary?: string;
  error?: string;
}

/** Pure display component — no state, no side effects. */
export default function StatusCard({ status, summary, error }: Props) {
  if (status === "idle") return null;

  if (status === "loading") {
    return (
      <div className="mt-6 flex flex-col items-center gap-3 rounded-xl border border-white/10 bg-white/5 p-8">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-white/20 border-t-brand-highlight" />
        <p className="text-sm text-white/60">Analyzing your data and generating summary…</p>
      </div>
    );
  }

  if (status === "error") {
    return (
      <div className="mt-6 rounded-xl border border-red-500/30 bg-red-500/10 p-5">
        <p className="text-sm font-medium text-red-400">Something went wrong</p>
        <p className="mt-1 text-sm text-white/60">{error ?? "An unexpected error occurred."}</p>
      </div>
    );
  }

  // success
  return (
    <div className="mt-6 rounded-xl border border-green-500/30 bg-green-500/10 p-5">
      <div className="mb-3 flex items-center gap-2">
        <span className="text-green-400">✓</span>
        <p className="text-sm font-semibold text-green-400">Summary sent to your inbox!</p>
      </div>
      {summary && (
        <div className="mt-3 rounded-lg border border-white/5 bg-black/20 p-4">
          <p className="mb-1 text-xs font-medium uppercase tracking-wider text-white/40">
            AI Summary
          </p>
          {/* Render each paragraph on its own line */}
          {summary.split("\n\n").map((para, i) => (
            <p key={i} className="mt-2 text-sm leading-relaxed text-white/80">
              {para}
            </p>
          ))}
        </div>
      )}
    </div>
  );
}
