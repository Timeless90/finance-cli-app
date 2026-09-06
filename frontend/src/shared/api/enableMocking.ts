import { apiConfig } from '@/shared/api/config';

export async function enableMocking() {
  if (apiConfig.mode !== 'mock' || import.meta.env.MODE === 'test') {
    return;
  }

  const { worker } = await import('@/shared/mocks/browser');
  await worker.start({
    onUnhandledRequest: 'bypass',
    serviceWorker: { url: '/mockServiceWorker.js' },
  });
}
