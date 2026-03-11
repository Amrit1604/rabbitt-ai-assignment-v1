"use client";

import { useRef, useState } from "react";

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

  function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    setDragOver(false);
    handleFile(e.dataTransfer.files[0] ?? null);
  }

  function handleSubmit(e: React.FormEvent) {
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
          cursor-pointer rounded-xl border-2 border-dashed px-6 py-10 text-center
          transition-colors duration-200
          ${dragOver ? "border-brand-highlight bg-brand-highlight/5" : "border-white/20 hover:border-white/40"}
        `}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".csv,.xlsx"
          className="hidden"
          onChange={(e) => handleFile(e.target.files?.[0] ?? null)}
        />
        <div className="mb-2 text-3xl">📁</div>
        {file ? (
          <p className="text-sm font-medium text-white">{file.name}</p>
        ) : (
          <>
            <p className="text-sm font-medium text-white">
              Drag & drop your file here, or click to browse
            </p>
            <p className="mt-1 text-xs text-white/50">CSV or XLSX — max 5 MB</p>
          </>
        )}
      </div>

      {/* Email input */}
      <div>
        <label htmlFor="email" className="mb-1.5 block text-sm font-medium text-white/80">
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
            w-full rounded-lg border border-white/10 bg-white/5 px-4 py-2.5
            text-sm text-white placeholder-white/30 outline-none
            focus:border-brand-highlight focus:ring-1 focus:ring-brand-highlight
            transition-colors
          "
        />
      </div>

      {/* Submit */}
      <button
        type="submit"
        disabled={!file || !email || isLoading}
        className="
          w-full rounded-lg bg-brand-highlight px-4 py-3 text-sm font-semibold text-white
          transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40
        "
      >
        {isLoading ? "Analyzing…" : "Generate & Send Summary"}
      </button>
    </form>
  );
}
