"use client";

import { useState } from "react";
import StatusCard from "@/components/StatusCard";
import UploadForm from "@/components/UploadForm";
import { analyzeFile } from "@/lib/api";
import type { UploadStatus } from "@/types";

export default function HomePage() {
  const [status, setStatus] = useState<UploadStatus>("idle");
  const [summary, setSummary] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(file: File, email: string) {
    setStatus("loading");
    setSummary("");
    setError("");

    try {
      const result = await analyzeFile(file, email);
      setSummary(result.summary);
      setStatus("success");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
      setStatus("error");
    }
  }

  return (
    <main className="min-h-screen bg-brand-dark px-4 py-16">
      <div className="mx-auto max-w-lg">
        {/* Header */}
        <div className="mb-10 text-center">
          <h1 className="text-3xl font-bold tracking-tight text-white">
            Sales Insight Automator
          </h1>
          <p className="mt-2 text-sm text-white/50">
            Upload your sales data. Get an AI-generated executive summary in your inbox.
          </p>
        </div>

        {/* Card */}
        <div className="rounded-2xl border border-white/10 bg-white/5 p-6 shadow-2xl backdrop-blur-sm">
          <UploadForm onSubmit={handleSubmit} isLoading={status === "loading"} />
          <StatusCard status={status} summary={summary} error={error} />
        </div>

        <p className="mt-6 text-center text-xs text-white/30">
          Supports CSV &amp; XLSX · Max 5 MB · Powered by Gemini + Groq
        </p>
      </div>
    </main>
  );
}
