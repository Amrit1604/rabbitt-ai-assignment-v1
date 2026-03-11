import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone", // needed for the multi-stage Docker build

  // Expose the backend URL to the browser bundle
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000",
  },
};

export default nextConfig;
