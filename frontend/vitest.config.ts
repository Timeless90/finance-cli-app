import { mergeConfig } from 'vite';
import { defineConfig } from 'vitest/config';

import { createViteConfig } from './vite.config';

export default mergeConfig(
  createViteConfig('test'),
  defineConfig({
    test: {
      environment: 'jsdom',
      environmentOptions: {
        jsdom: {
          url: 'http://localhost/',
        },
      },
      setupFiles: ['./src/shared/test/setup.ts'],
      include: ['src/**/*.test.{ts,tsx}'],
      css: true,
      coverage: {
        provider: 'v8',
        reporter: ['text', 'json', 'cobertura'],
        include: ['src/**/*.{ts,tsx}'],
        exclude: [
          'src/generated/**',
          'src/**/*.stories.tsx',
          'src/shared/test/**',
          'src/shared/mocks/**',
          'src/main.tsx',
        ],
        thresholds: { lines: 80, statements: 80, functions: 80, branches: 80 },
      },
    },
  }),
);
