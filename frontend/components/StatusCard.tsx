import { motion } from "framer-motion";
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
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="mt-6 flex flex-col items-center gap-4 rounded-2xl border border-border bg-muted p-8 text-center"
      >
        <div className="relative h-10 w-10">
          <div className="absolute inset-0 rounded-full border-2 border-border" />
          <div className="absolute inset-0 animate-spin rounded-full border-2 border-transparent border-t-accent" />
        </div>
        <div>
          <p className="text-sm font-medium text-foreground">Analysing your data…</p>
          <p className="mt-1 text-xs text-muted-foreground">
            Gemini is generating your executive summary
          </p>
        </div>
      </motion.div>
    );
  }

  if (status === "error") {
    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="mt-6 rounded-2xl border border-red-200 bg-red-50 p-5"
      >
        <div className="flex items-start gap-3">
          <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-red-100 text-red-500 text-xs font-bold">
            !
          </span>
          <div>
            <p className="text-sm font-semibold text-red-700">Analysis failed</p>
            <p className="mt-1 text-sm text-red-600/80">
              {error ?? "An unexpected error occurred. Please try again."}
            </p>
          </div>
        </div>
      </motion.div>
    );
  }

  // success
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="mt-6 overflow-hidden rounded-2xl border border-border bg-card shadow-sm"
    >
      {/* Gradient top bar */}
      <div className="gradient-bg h-1 w-full" />

      <div className="p-5">
        <div className="flex items-center gap-2">
          <span className="flex h-5 w-5 items-center justify-center rounded-full bg-accent/10 text-accent text-xs font-bold">
            ✓
          </span>
          <p className="text-sm font-semibold text-foreground">
            Summary sent to your inbox!
          </p>
        </div>

        {summary && (
          <div className="mt-4 rounded-xl border border-border bg-muted p-4">
            <p className="mb-2 font-mono text-[10px] font-medium uppercase tracking-widest text-muted-foreground">
              AI Summary Preview
            </p>
            <div className="space-y-2">
              {summary.split("\n\n").map((para, i) => (
                <p key={i} className="text-sm leading-relaxed text-foreground/80">
                  {para}
                </p>
              ))}
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
}

