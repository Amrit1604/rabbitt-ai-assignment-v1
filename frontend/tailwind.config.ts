import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#FAFAFA",
        foreground: "#0F172A",
        muted: "#F1F5F9",
        "muted-foreground": "#64748B",
        accent: "#0052FF",
        "accent-secondary": "#4D7CFF",
        "accent-foreground": "#FFFFFF",
        border: "#E2E8F0",
        card: "#FFFFFF",
      },
      fontFamily: {
        display: ["var(--font-calistoga)", "Georgia", "serif"],
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "monospace"],
      },
      boxShadow: {
        accent: "0 4px 14px rgba(0,82,255,0.25)",
        "accent-lg": "0 8px 24px rgba(0,82,255,0.35)",
      },
      animation: {
        "spin-slow": "spin 60s linear infinite",
        "float-a": "floatA 5s ease-in-out infinite",
        "float-b": "floatB 4s ease-in-out infinite",
        "pulse-dot": "pulseDot 2s ease-in-out infinite",
      },
      keyframes: {
        floatA: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-10px)" },
        },
        floatB: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(10px)" },
        },
        pulseDot: {
          "0%, 100%": { transform: "scale(1)", opacity: "1" },
          "50%": { transform: "scale(1.3)", opacity: "0.7" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
