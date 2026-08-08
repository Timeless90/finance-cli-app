import "@testing-library/jest-dom/vitest";

import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { TacticalFrame } from "./tactical-frame";

describe("TacticalFrame", () => {
  it("renders its label and content", () => {
    render(
      <TacticalFrame label="RISK COMMAND" tone="active">
        <p>Ready</p>
      </TacticalFrame>,
    );

    expect(screen.getByText("RISK COMMAND")).toBeInTheDocument();
    expect(screen.getByText("Ready")).toBeInTheDocument();
  });
});
