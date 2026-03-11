"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import StatusCard from "@/components/StatusCard";
import UploadForm from "@/components/UploadForm";
import { analyzeFile } from "@/lib/api";
import type { UploadStatus } from "@/types";

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  show: (delay = 0) => ({
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, ease: "easeOut", delay },
  }),
};

const steps = [
  {
    num: "01",
    title: "Upload your file",
    desc: "Drop a CSV or XLSX export from any CRM or spreadsheet tool.",
  },
  {
    num: "02",
    title: "AI analyses the data",
    desc: "Gemini 1.5 Flash reads revenue trends, top regions, and anomalies.",
  },
  {
    num: "03",
    title: "Summary hits your inbox",
    desc: "A polished executive summary is emailed directly to you.",
  },
];

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
    <div className="min-h-screen bg-background text-foreground">
      {/* ─── Nav ─── */}
      <header className="border-b border-border bg-card/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
          <span className="font-display text-lg font-normal tracking-tight text-foreground">
            Rabbitt<span className="gradient-text">AI</span>
          </span>
          <span className="rounded-full border border-border bg-muted px-3 py-1 text-xs font-medium text-muted-foreground">
            Assignment v1
          </span>
        </div>
      </header>

      <main>
        {/* ─── Hero ─── */}
        <section className="px-6 pb-20 pt-20 text-center">
          <div className="mx-auto max-w-3xl">
            {/* Badge */}
            <motion.div
              variants={fadeUp}
              initial="hidden"
              animate="show"
              custom={0}
              className="mb-8 inline-flex items-center gap-2 rounded-full border border-border bg-card px-4 py-1.5 shadow-sm"
            >
              <span className="inline-block h-2 w-2 animate-pulse-dot rounded-full bg-accent" />
              <span className="text-xs font-medium text-muted-foreground">
                Powered by Gemini 1.5 Flash · Groq fallback
              </span>
            </motion.div>

            {/* Headline */}
            <motion.h1
              variants={fadeUp}
              initial="hidden"
              animate="show"
              custom={0.1}
              className="font-display text-5xl font-normal leading-tight tracking-tight text-foreground sm:text-6xl"
            >
              Turn sales data into{" "}
              <span className="gradient-text">insights</span>
              <br />
              in seconds.
            </motion.h1>

            <motion.p
              variants={fadeUp}
              initial="hidden"
              animate="show"
              custom={0.2}
              className="mx-auto mt-6 max-w-xl text-base leading-relaxed text-muted-foreground"
            >
              Upload a CSV or XLSX file. Our AI extracts trends, highlights top
              performers, and emails you a clean executive summary — no dashboards,
              no noise.
            </motion.p>
          </div>
        </section>

        {/* ─── Upload card ─── */}
        <section className="px-6 pb-24">
          <motion.div
            variants={fadeUp}
            initial="hidden"
            animate="show"
            custom={0.3}
            className="mx-auto max-w-lg rounded-2xl border border-border bg-card p-8 shadow-sm"
          >
            <UploadForm onSubmit={handleSubmit} isLoading={status === "loading"} />
            <StatusCard status={status} summary={summary} error={error} />
          </motion.div>
          <p className="mt-4 text-center text-xs text-muted-foreground">
            Supports CSV &amp; XLSX · Max 5 MB · Data is never stored
          </p>
        </section>

        {/* ─── How it works ─── */}
        <section className="border-t border-border bg-muted px-6 py-20">
          <div className="mx-auto max-w-4xl">
            <motion.div
              variants={fadeUp}
              initial="hidden"
              whileInView="show"
              viewport={{ once: true }}
              custom={0}
              className="mb-12 text-center"
            >
              <h2 className="font-display text-3xl font-normal text-foreground">
                How it works
              </h2>
              <p className="mt-3 text-sm text-muted-foreground">
                Three steps from upload to inbox.
              </p>
            </motion.div>

            <div className="grid gap-6 sm:grid-cols-3">
              {steps.map((step, i) => (
                <motion.div
                  key={step.num}
                  variants={fadeUp}
                  initial="hidden"
                  whileInView="show"
                  viewport={{ once: true }}
                  custom={i * 0.1}
                  className="rounded-2xl border border-border bg-card p-6 shadow-sm"
                >
                  <span className="font-mono text-xs font-medium text-accent">
                    {step.num}
                  </span>
                  <h3 className="mt-3 text-base font-semibold text-foreground">
                    {step.title}
                  </h3>
                  <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                    {step.desc}
                  </p>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* ─── Dark stats band ─── */}
        <section className="bg-foreground px-6 py-16 text-center">
          <div className="mx-auto max-w-3xl">
            <p className="font-display text-2xl font-normal text-white sm:text-3xl">
              Built for sales teams who move fast.
            </p>
            <p className="mt-4 text-sm text-white/50">
              No logins. No data retention. Just upload, analyse, and act.
            </p>
            <div className="mx-auto mt-10 grid max-w-xl grid-cols-3 gap-6">
              {[
                { val: "< 10s", label: "Average analysis time" },
                { val: "2 LLMs", label: "Gemini + Groq fallback" },
                { val: "0 stored", label: "Files kept after scan" },
              ].map((stat) => (
                <div key={stat.label}>
                  <p className="gradient-text text-3xl font-semibold">{stat.val}</p>
                  <p className="mt-1 text-xs text-white/40">{stat.label}</p>
                </div>
              ))}
            </div>
          </div>
        </section>
      </main>

      {/* ─── Footer ─── */}
      <footer className="border-t border-border bg-card px-6 py-8 text-center">
        <p className="text-xs text-muted-foreground">
          © 2026 Rabbitt AI · Built with Next.js, FastAPI &amp; Gemini
        </p>
      </footer>
    </div>
  );
}
