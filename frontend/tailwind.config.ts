import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          dark: "#1a1a2e",
          mid: "#16213e",
          accent: "#0f3460",
          highlight: "#e94560",
        },
      },
    },
  },
  plugins: [],
};

export default config;
