import { afterEach, describe, expect, it, vi } from 'vitest'

import { listCustomers } from './customers'

describe('customers api client reliability', () => {
  afterEach(() => {
    vi.restoreAllMocks()
    vi.useRealTimers()
  })

  it('fails fast on network failure without retrying', async () => {
    const fetchMock = vi
      .fn()
      .mockRejectedValueOnce(new TypeError('network down'))
    vi.stubGlobal('fetch', fetchMock)

    await expect(listCustomers({ page: 1, limit: 10 })).rejects.toMatchObject({
      code: 'network_error',
    })
    expect(fetchMock).toHaveBeenCalledTimes(1)
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
