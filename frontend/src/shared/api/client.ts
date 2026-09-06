import { dispatch, type ResponseData } from '@/generated/dispatch';
import { ApiContractError } from './errors';

export type ClientOptions = {
  params?: { path?: Record<string, string | number>; query?: Record<string, unknown> };
  body?: unknown;
  headers?: HeadersInit;
  signal?: AbortSignal;
  request?: RequestInit;
};
type Result<T> = { data?: T; error?: unknown; response: Response };
type GetPath = keyof ResponseData extends infer K
  ? K extends `GET ${infer P}`
    ? P
    : never
  : never;
type PostPath = keyof ResponseData extends infer K
  ? K extends `POST ${infer P}`
    ? P
    : never
  : never;

export function createApiClient(fetchFn?: typeof fetch) {
  async function call(
    method: string,
    path: string,
    options: ClientOptions = {},
  ): Promise<Result<unknown>> {
    const key = `${method} ${path}` as keyof typeof dispatch;
    const operation = dispatch[key];
    if (!operation) throw new Error(`Unknown API operation: ${key}`);
    try {
      const request = {
        ...(options.headers ? { headers: options.headers } : {}),
        ...options.request,
        ...(options.signal ? { signal: options.signal } : {}),
        ...(fetchFn ? { fetchFn } : {}),
      };
      const result = await operation({ ...options, request });
      return {
        data: result.data,
        response: new Response(null, {
          status: result.status,
          headers: result.headers,
        }),
      };
    } catch (error) {
      if (!(error instanceof ApiContractError) || error.status === null) throw error;
      return {
        error: error.payload,
        response: new Response(null, { status: error.status }),
      };
    }
  }
  return {
    GET: <P extends GetPath>(path: P, options?: ClientOptions) =>
      call('GET', path, options) as Promise<Result<ResponseData[`GET ${P}`]>>,
    POST: <P extends PostPath>(path: P, options?: ClientOptions) =>
      call('POST', path, options) as Promise<Result<ResponseData[`POST ${P}`]>>,
  };
}
export type ApiClient = ReturnType<typeof createApiClient>;
export const apiClient = createApiClient();
