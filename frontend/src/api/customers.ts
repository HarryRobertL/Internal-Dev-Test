import type {
  ApiEnvelope,
  Customer,
  CustomerCreateInput,
  CustomerListData,
  PaginationMeta,
} from '../types/customer'

const DEFAULT_API_URL = 'http://localhost:8000'
const API_BASE_URL =
  import.meta.env.VITE_API_URL?.replace(/\/$/, '') ?? DEFAULT_API_URL
const REQUEST_TIMEOUT_MS = 8000
const MAX_ATTEMPTS = 2
const RETRY_DELAY_MS = 250

export class ApiError extends Error {
  readonly status: number
  readonly code: string
  readonly details: unknown

  constructor(params: {
    status: number
    code: string
    message: string
    details: unknown
  }) {
    super(params.message)
    this.name = 'ApiError'
    this.status = params.status
    this.code = params.code
    this.details = params.details
  }
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => {
    setTimeout(resolve, ms)
  })
}

function isAbortError(error: unknown): boolean {
  return error instanceof DOMException && error.name === 'AbortError'
}

function shouldRetry(error: ApiError): boolean {
  if (error.code === 'network_error' || error.code === 'timeout_error') return true
  if (error.status >= 500) return true
  return false
}

async function fetchWithTimeout(
  url: string,
  init?: RequestInit,
): Promise<Response> {
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS)

  const externalSignal = init?.signal
  const onAbort = () => controller.abort()
  if (externalSignal) {
    if (externalSignal.aborted) {
      clearTimeout(timeoutId)
      throw new ApiError({
        status: 0,
        code: 'request_cancelled',
        message: 'Request was cancelled.',
        details: null,
      })
    }
    externalSignal.addEventListener('abort', onAbort, { once: true })
  }

  try {
    return await fetch(url, {
      ...init,
      signal: controller.signal,
    })
  } catch (error) {
    if (isAbortError(error)) {
      if (externalSignal?.aborted) {
        throw new ApiError({
          status: 0,
          code: 'request_cancelled',
          message: 'Request was cancelled.',
          details: null,
        })
      }
      throw new ApiError({
        status: 0,
        code: 'timeout_error',
        message: 'The request timed out. Please try again.',
        details: { timeout_ms: REQUEST_TIMEOUT_MS },
      })
    }
    throw new ApiError({
      status: 0,
      code: 'network_error',
      message: 'Unable to reach the API. Please check your connection.',
      details: null,
    })
  } finally {
    clearTimeout(timeoutId)
    externalSignal?.removeEventListener('abort', onAbort)
  }
}

async function requestJson<T>(
  path: string,
  init?: RequestInit,
): Promise<ApiEnvelope<T>> {
  let lastError: ApiError | null = null
  for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt += 1) {
    try {
      const response = await fetchWithTimeout(`${API_BASE_URL}${path}`, {
        ...init,
        headers: {
          'Content-Type': 'application/json',
          ...(init?.headers ?? {}),
        },
      })

      const text = await response.text()
      let parsed: unknown = null
      if (text) {
        try {
          parsed = JSON.parse(text) as unknown
        } catch {
          parsed = null
        }
      }

      if (!response.ok) {
        const errorBody = parsed as ApiEnvelope<null> | null
        throw new ApiError({
          status: response.status,
          code: errorBody?.error?.code ?? 'http_error',
          message: errorBody?.error?.message ?? 'Request failed',
          details: errorBody?.error?.details ?? null,
        })
      }

      return parsed as ApiEnvelope<T>
    } catch (error) {
      const apiError =
        error instanceof ApiError
          ? error
          : new ApiError({
              status: 0,
              code: 'network_error',
              message: 'Unable to reach the API. Please check your connection.',
              details: null,
            })

      lastError = apiError
      const canRetry = attempt < MAX_ATTEMPTS && shouldRetry(apiError)
      if (canRetry) {
        await sleep(RETRY_DELAY_MS)
        continue
      }

      if (attempt > 1 && shouldRetry(apiError)) {
        throw new ApiError({
          status: apiError.status,
          code: 'retry_exhausted',
          message: 'Request failed after retrying. Please try again.',
          details: {
            cause: apiError.code,
            attempts: attempt,
          },
        })
      }
      throw apiError
    }
  }

  throw (
    lastError ??
    new ApiError({
      status: 0,
      code: 'network_error',
      message: 'Unable to reach the API. Please check your connection.',
      details: null,
    })
  )
}

export async function createCustomer(
  payload: CustomerCreateInput,
): Promise<Customer> {
  const response = await requestJson<Customer>('/api/customers', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
  if (!response.data) {
    throw new ApiError({
      status: 500,
      code: 'invalid_contract',
      message: 'API returned an invalid success envelope.',
      details: response,
    })
  }
  return response.data
}

export async function getCustomerById(customerId: string): Promise<Customer> {
  const response = await requestJson<Customer>(`/api/customers/${customerId}`)
  if (!response.data) {
    throw new ApiError({
      status: 500,
      code: 'invalid_contract',
      message: 'API returned an invalid success envelope.',
      details: response,
    })
  }
  return response.data
}

export async function listCustomers(params: {
  page: number
  limit: number
  signal?: AbortSignal
}): Promise<CustomerListData> {
  const query = new URLSearchParams({
    page: String(params.page),
    limit: String(params.limit),
  })
  const response = await requestJson<Customer[]>(
    `/api/customers?${query.toString()}`,
    { signal: params.signal },
  )
  const pagination = response.meta?.pagination as PaginationMeta | null
  if (!response.data || !pagination) {
    throw new ApiError({
      status: 500,
      code: 'invalid_contract',
      message: 'API returned an invalid list envelope.',
      details: response,
    })
  }
  return {
    items: response.data,
    pagination,
  }
}
