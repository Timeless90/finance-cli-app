import { defineConfig } from 'orval';
export default defineConfig({
  api: {
    input: '../backend/openapi.json',
    output: {
      target: './src/generated/api.ts',
      schemas: './src/generated/models',
      client: 'react-query',
      httpClient: 'fetch',
      clean: true,
      override: { mutator: { path: './src/shared/lib/fetcher.ts', name: 'apiFetch' } },
    },
  },
});
