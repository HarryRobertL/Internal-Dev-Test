import { afterEach, describe, expect, it, vi } from 'vitest'

import { listCustomers } from './customers'

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

describe('customers api client reliability', () => {
  afterEach(() => {
    vi.restoreAllMocks()
    vi.useRealTimers()
  })

  it('retries once on network failure and succeeds on second attempt', async () => {
    const fetchMock = vi
      .fn()
      .mockRejectedValueOnce(new TypeError('network down'))
      .mockResolvedValueOnce(
        jsonResponse({
          data: [],
          error: null,
          meta: {
            pagination: { page: 1, limit: 10, total: 0, total_pages: 0 },
          },
        }),
      )
    vi.stubGlobal('fetch', fetchMock)

    const result = await listCustomers({ page: 1, limit: 10 })
    expect(fetchMock).toHaveBeenCalledTimes(2)
    expect(result).toEqual({
      items: [],
      pagination: { page: 1, limit: 10, total: 0, total_pages: 0 },
    })
  })

  it('returns retry_exhausted after repeated timeouts', async () => {
    vi.useFakeTimers()
    const fetchMock = vi.fn((_url: string, init?: RequestInit) => {
      return new Promise<Response>((_resolve, reject) => {
        const signal = init?.signal
        signal?.addEventListener(
          'abort',
          () => reject(new DOMException('Aborted', 'AbortError')),
          { once: true },
        )
      })
    })
    vi.stubGlobal('fetch', fetchMock)

    const request = listCustomers({ page: 1, limit: 10 })
    const rejection = expect(request).rejects.toMatchObject({
      code: 'retry_exhausted',
    })
    await vi.advanceTimersByTimeAsync(17000)

    await rejection
    expect(fetchMock).toHaveBeenCalledTimes(2)
  })
})
