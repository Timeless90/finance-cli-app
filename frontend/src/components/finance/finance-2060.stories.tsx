import type { Meta, StoryObj } from "@storybook/react-vite";

import { Button } from "@/components/ui/button";

import { MetricPanel } from "./metric-panel";
import { StatusIndicator } from "./status-indicator";
import { TacticalFrame } from "./tactical-frame";

const meta = {
  title: "Finance 2060/Foundations",
  component: TacticalFrame,
  parameters: {
    layout: "fullscreen",
  },
} satisfies Meta<typeof TacticalFrame>;

export default meta;
type Story = StoryObj<typeof meta>;

export const SystemPreview: Story = {
  render: () => (
    <div className="ds-environment min-h-screen p-8">
      <div className="mx-auto grid max-w-5xl gap-5">
        <TacticalFrame
          label="FINANCE 2060 // COMPONENT SYSTEM"
          tone="active"
          labelAction={<StatusIndicator label="SYSTEM" detail="NOMINAL" tone="positive" />}
        >
          <div className="grid gap-4 p-5 md:grid-cols-3">
            <MetricPanel label="EBITDA" value="€184.2M" delta="+8.4%" deltaTone="positive" />
            <MetricPanel label="CASH" value="€92.4M" delta="+€4.8M" deltaTone="positive" />
            <MetricPanel label="VAR 95%" value="€13.6M" delta="-2.1%" deltaTone="negative" />
          </div>
          <div className="flex flex-wrap gap-3 border-t border-[var(--frame-muted)] p-5">
            <Button>RUN SCENARIO</Button>
            <Button variant="outline">OPEN ANALYSIS</Button>
          </div>
        </TacticalFrame>
      </div>
    </div>
  ),
};
