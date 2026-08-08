import "@testing-library/jest-dom/vitest";

import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { App } from "@/app/App";

describe("App", () => {
  it("renders the frontend foundation status", () => {
    render(<App />);

    expect(
      screen.getByRole("heading", { name: "Frontend foundation online." }),
    ).toBeInTheDocument();
    expect(screen.getByText("/api/v1")).toBeInTheDocument();
  });
});
