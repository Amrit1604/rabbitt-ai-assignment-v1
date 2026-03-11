import type { AnalyzeResponse, ApiError } from "@/types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

/**
 * POST /api/analyze
 * Sends the sales file and recipient email to the backend.
 * Throws an Error with a user-facing message on any failure.
 */
export async function analyzeFile(file: File, email: string): Promise<AnalyzeResponse> {
  const body = new FormData();
  body.append("file", file);
  body.append("email", email);

  const response = await fetch(`${BASE_URL}/api/analyze`, {
    method: "POST",
    body,
  });

  if (!response.ok) {
    const err: ApiError = await response.json().catch(() => ({
      detail: "Something went wrong. Please try again.",
    }));
    throw new Error(err.detail ?? "Request failed.");
  }

  return response.json() as Promise<AnalyzeResponse>;
}
