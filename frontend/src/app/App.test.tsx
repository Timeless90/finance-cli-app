import "@testing-library/jest-dom/vitest";

import { render, screen } from "@testing-library/react";
import { RouterProvider, createMemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";

import { AppShell } from "@/components/layout";
import { WorkspacePlaceholder } from "@/pages/WorkspacePlaceholder";

describe("FE-02 application shell", () => {
  it("renders command center navigation and local context", () => {
    const router = createMemoryRouter(
      [
        {
          path: "/app",
          element: <AppShell />,
          children: [{ path: "command-center", element: <WorkspacePlaceholder /> }],
        },
      ],
      { initialEntries: ["/app/command-center"] },
    );

    render(<RouterProvider router={router} />);

    expect(screen.getByRole("heading", { name: "Command Center" })).toBeInTheDocument();
    expect(screen.getByText(/LOCAL CONTEXT/)).toBeInTheDocument();
    expect(screen.getAllByText("UNBOUND").length).toBeGreaterThan(0);
  });
});
