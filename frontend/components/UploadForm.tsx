"use client";

import type { DragEvent, FormEvent } from "react";
import { useRef, useState } from "react";
import { motion } from "framer-motion";

interface Props {
  onSubmit: (file: File, email: string) => void;
  isLoading: boolean;
}

const ACCEPTED = [".csv", ".xlsx"];

export default function UploadForm({ onSubmit, isLoading }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [email, setEmail] = useState("");
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  function handleFile(selected: File | null) {
    if (!selected) return;
    const ext = selected.name.slice(selected.name.lastIndexOf(".")).toLowerCase();
    if (!ACCEPTED.includes(ext)) {
      alert("Only .csv and .xlsx files are supported.");
      return;
    }
    setFile(selected);
  }

  function handleDrop(e: DragEvent<HTMLDivElement>) {
    e.preventDefault();
    setDragOver(false);
    handleFile(e.dataTransfer.files[0] ?? null);
  }

  function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!file || !email) return;
    onSubmit(file, email);
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {/* Drop zone */}
      <div
        onClick={() => inputRef.current?.click()}
        onDrop={handleDrop}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        className={`
          cursor-pointer select-none rounded-2xl border-2 border-dashed px-6 py-10 text-center
          transition-all duration-200
          ${dragOver
            ? "border-accent bg-accent/5 shadow-accent"
            : file
              ? "border-accent/40 bg-accent/[0.03]"
              : "border-border bg-muted hover:border-accent/40"
          }
        `}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".csv,.xlsx"
          className="hidden"
          onChange={(e) => handleFile(e.target.files?.[0] ?? null)}
        />

        <div className="mb-3 flex justify-center">
          <div className={`rounded-xl p-3 ${file ? "bg-accent/10" : "bg-border"}`}>
            <svg
              className={`h-6 w-6 ${file ? "text-accent" : "text-muted-foreground"}`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={1.5}
            >
              {file ? (
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m6.75 12-3-3m0 0-3 3m3-3v6m-1.5-15H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
              )}
            </svg>
          </div>
        </div>

        {file ? (
          <>
            <p className="text-sm font-semibold text-foreground">{file.name}</p>
            <p className="mt-1 text-xs text-muted-foreground">
              {(file.size / 1024).toFixed(1)} KB · Click to change
            </p>
          </>
        ) : (
          <>
            <p className="text-sm font-semibold text-foreground">
              Drop your file here, or{" "}
              <span className="text-accent underline underline-offset-2">browse</span>
            </p>
            <p className="mt-1 text-xs text-muted-foreground">CSV or XLSX — max 5 MB</p>
          </>
        )}
      </div>

      {/* Email input */}
      <div>
        <label htmlFor="email" className="mb-2 block text-sm font-medium text-foreground">
          Recipient email
        </label>
        <input
          id="email"
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="you@company.com"
          className="
            h-12 w-full rounded-xl border border-border bg-background px-4
            text-sm text-foreground placeholder-muted-foreground outline-none
            transition-all focus:border-accent focus:ring-2 focus:ring-accent/20
          "
        />
      </div>

      {/* Submit */}
      <motion.button
        type="submit"
        disabled={!file || !email || isLoading}
        whileHover={!isLoading && file && email ? { y: -2, boxShadow: "0 8px 24px rgba(0,82,255,0.35)" } : {}}
        whileTap={!isLoading && file && email ? { scale: 0.98 } : {}}
        className="
          gradient-bg h-12 w-full rounded-xl text-sm font-semibold text-white
          shadow-accent transition-shadow duration-200
          disabled:cursor-not-allowed disabled:opacity-40
        "
      >
        {isLoading ? (
          <span className="flex items-center justify-center gap-2">
            <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
            Analysing…
          </span>
        ) : (
          "Generate & Send Summary →"
        )}
      </motion.button>
    </form>
  );
}

