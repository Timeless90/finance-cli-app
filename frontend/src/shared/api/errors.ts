export class ApiContractError extends Error {
  constructor(
    message: string,
    readonly status: number | null,
    readonly payload: unknown,
  ) {
    super(message);
    this.name = 'ApiContractError';
  }
}

export function toApiContractError(response: Response | undefined, payload: unknown) {
  const status = response?.status ?? null;
  const suffix = status === null ? 'without an HTTP response' : `with HTTP ${status}`;
  return new ApiContractError(
    `Backend contract request failed ${suffix}.`,
    status,
    payload,
  );
}

export function describeApiError(error: unknown, resource: string): string {
  const status = error instanceof ApiContractError ? error.status : null;
  if (status === 401)
    return 'Your session is not authorized. Sign in again to continue.';
  if (status === 403)
    return `You do not have access to this ${resource.toLowerCase()} for the selected company.`;
  if (status === 404)
    return `No published ${resource.toLowerCase()} is available for this context.`;
  if (status === 422) return 'The selected company, period, or scenario is not valid.';
  if (status === 429)
    return 'The platform is busy. Please wait a moment before retrying.';
  if (status === 503)
    return 'The platform is temporarily unavailable. Please try again.';
  return `${resource} is unavailable.`;
}
