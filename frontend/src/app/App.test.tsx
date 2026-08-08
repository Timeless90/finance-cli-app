import "@testing-library/jest-dom/vitest";

import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";

import { App } from "@/app/App";

describe("FE-04 public landing", () => {
  it("renders the public finance 2060 experience without backend data", () => {
    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>,
    );

    expect(screen.getByRole("heading", { name: /see the future of finance/i })).toBeInTheDocument();
    expect(screen.getAllByText(/simulated ui preview/i).length).toBeGreaterThan(0);
    expect(screen.getByRole("link", { name: "LAUNCH COMMAND CENTER" })).toHaveAttribute(
      "href",
      "/app/command-center",
    );
  });
});
