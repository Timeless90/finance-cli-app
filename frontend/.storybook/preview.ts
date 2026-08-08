import type { Preview } from "@storybook/react-vite";

import "../src/styles/global.css";

const preview: Preview = {
  parameters: {
    backgrounds: {
      default: "cfo-canvas",
      values: [{ name: "cfo-canvas", value: "#050505" }],
    },
  },
};

export default preview;
