import { apiConfig } from "@/api/config";

export async function enableMocking() {
  if (apiConfig.mode !== "mock" || import.meta.env.MODE === "test") {
    return;
  }

  const { worker } = await import("@/mocks/browser");
  await worker.start({
    onUnhandledRequest: "bypass",
    serviceWorker: { url: "/mockServiceWorker.js" },
  });
}
