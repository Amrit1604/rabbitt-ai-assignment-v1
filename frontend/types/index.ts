/** Upload status drives the UI state machine */
export type UploadStatus = "idle" | "loading" | "success" | "error";

/** Shape of a successful response from POST /api/analyze */
export interface AnalyzeResponse {
  message: string;
  summary: string;
}

/** Shape of an error response from the backend */
export interface ApiError {
  detail: string;
}
