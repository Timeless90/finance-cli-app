import { fileURLToPath, URL } from 'node:url';

import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';
import { defineConfig, loadEnv, type ProxyOptions, type UserConfig } from 'vite';

export function createViteConfig(mode: string): UserConfig {
  const env = loadEnv(mode, process.cwd(), '');
  const useUatGateway = mode === 'uat' && env.CFO_UAT_GATEWAY === 'true';
  const useLocalGateway = mode === 'devlocal' && env.CFO_LOCAL_GATEWAY === 'true';
  const uatHeaders = {
    'X-User': env.CFO_UAT_USER ?? 'uat-cfo',
    'X-Roles': env.CFO_UAT_ROLES ?? 'cfo',
    'X-Companies': env.CFO_UAT_COMPANIES ?? 'AURELIA,EUROPE',
  };
  const apiProxy: ProxyOptions = {
    target: env.CFO_API_TARGET || 'http://127.0.0.1:8000',
    changeOrigin: true,
  };
  if (useUatGateway || useLocalGateway) {
    apiProxy.configure = (proxy) => {
      proxy.on('proxyReq', (request) => {
        const localActor = String(
          request.getHeader('X-Local-Actor') ?? 'developer',
        ).toLowerCase();
        const localProfiles = {
          developer: uatHeaders,
          reviewer: {
            'X-User': 'local-reviewer',
            'X-Roles': 'controller',
            'X-Companies': 'AURELIA,EUROPE',
          },
          approver: {
            'X-User': 'local-approver',
            'X-Roles': 'cfo',
            'X-Companies': 'AURELIA,EUROPE',
          },
        } as const;
        const headers = useLocalGateway
          ? (localProfiles[localActor as keyof typeof localProfiles] ??
            localProfiles.developer)
          : uatHeaders;
        request.removeHeader('X-Local-Actor');
        for (const header of Object.keys(uatHeaders)) {
          request.removeHeader(header);
          request.setHeader(header, headers[header as keyof typeof headers]);
        }
      });
    };
  }

  return {
    plugins: [react(), tailwindcss()],
    define: { 'import.meta.env.VITE_LOCAL_GATEWAY': JSON.stringify(useLocalGateway) },
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
    server: {
      host: '127.0.0.1',
      port: 5173,
      strictPort: true,
      proxy: {
        '/api': apiProxy,
        '/health': {
          target: env.CFO_API_TARGET || 'http://127.0.0.1:8000',
          changeOrigin: true,
        },
      },
    },
  };
}

export default defineConfig(({ mode }) => createViteConfig(mode));
