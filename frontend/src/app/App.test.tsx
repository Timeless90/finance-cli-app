import "@testing-library/jest-dom/vitest";

import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { App } from "@/app/App";

describe("App", () => {
  it("renders the Finance 2060 design system preview", () => {
    render(<App />);

    expect(screen.getByRole("heading", { name: "Tactical finance interface." })).toBeInTheDocument();
    expect(screen.getByText("NO BACKEND CONTRACT")).toBeInTheDocument();
    expect(screen.getByText("€184.2M")).toBeInTheDocument();
  });
});
