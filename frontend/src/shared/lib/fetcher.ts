import { apiConfig } from '@/shared/api/config';
import { ApiContractError } from '@/shared/api/errors';

export async function apiFetch<T>(
  url: string,
  options: RequestInit & { fetchFn?: typeof fetch },
): Promise<T> {
  const headers = new Headers(options.headers);
  if (import.meta.env.VITE_LOCAL_GATEWAY && typeof window !== 'undefined') {
    headers.set(
      'X-Local-Actor',
      window.localStorage.getItem('cfo-local-actor') ?? 'developer',
    );
  }
  const response = await (options.fetchFn ?? fetch)(apiConfig.baseUrl + url, {
    ...options,
    headers,
  });
  const text = await response.text();
  let data: unknown;
  try {
    data = text ? JSON.parse(text) : undefined;
  } catch {
    data = text;
  }
  if (!response.ok)
    throw new ApiContractError(
      `Backend contract request failed with HTTP ${response.status}.`,
      response.status,
      data,
    );
  return { data, status: response.status, headers: response.headers } as T;
}
