export type ApiMode = "live" | "mock";

const requestedMode = import.meta.env.VITE_API_MODE ?? "live";

if (requestedMode !== "live" && requestedMode !== "mock") {
  throw new Error(`Unsupported VITE_API_MODE: ${requestedMode}`);
}

const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "");

export const apiConfig = {
  mode: requestedMode as ApiMode,
  baseUrl: configuredBaseUrl ?? (import.meta.env.MODE === "test" ? "http://localhost" : ""),
} as const;
