import React from "react";
import ReactDOM from "react-dom/client";
import { RouterProvider } from "react-router-dom";

import { enableMocking } from "@/api/enableMocking";
import { router } from "@/app/router";
import "@/styles/global.css";

async function bootstrap() {
  await enableMocking();

  const rootElement = document.getElementById("root");
  if (!rootElement) {
    throw new Error("Unable to initialize CFO Command Center: root element is missing.");
  }

  ReactDOM.createRoot(rootElement).render(
    <React.StrictMode>
      <RouterProvider router={router} />
    </React.StrictMode>,
  );
}

void bootstrap();
