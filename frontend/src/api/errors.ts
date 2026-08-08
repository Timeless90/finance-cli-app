export class ApiContractError extends Error {
  constructor(
    message: string,
    readonly status: number | null,
    readonly payload: unknown,
  ) {
    super(message);
    this.name = "ApiContractError";
  }
}

export function toApiContractError(response: Response | undefined, payload: unknown) {
  const status = response?.status ?? null;
  const suffix = status === null ? "without an HTTP response" : `with HTTP ${status}`;
  return new ApiContractError(`Backend contract request failed ${suffix}.`, status, payload);
}
