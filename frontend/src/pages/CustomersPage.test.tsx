import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { ApiError, createCustomer, listCustomers } from '../api/customers'
import { CustomersPage } from './CustomersPage'

vi.mock('../api/customers', async () => {
  const actual = await vi.importActual<typeof import('../api/customers')>(
    '../api/customers',
  )

  return {
    ...actual,
    createCustomer: vi.fn(),
    listCustomers: vi.fn(),
  }
})

const listCustomersMock = vi.mocked(listCustomers)
const createCustomerMock = vi.mocked(createCustomer)

function mockListResponse(overrides?: Partial<Awaited<ReturnType<typeof listCustomers>>>) {
  listCustomersMock.mockResolvedValue({
    items: [],
    pagination: { page: 1, limit: 10, total: 0, total_pages: 0 },
    ...overrides,
  })
}

function deferred<T>() {
  let resolve!: (value: T) => void
  let reject!: (reason?: unknown) => void

  const promise = new Promise<T>((res, rej) => {
    resolve = res
    reject = rej
  })

  return { promise, resolve, reject }
}

describe('CustomersPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockListResponse()
  })

  it('shows loading state while fetching the customer list', () => {
    const pending = deferred<Awaited<ReturnType<typeof listCustomers>>>()
    listCustomersMock.mockReturnValueOnce(pending.promise)

    render(<CustomersPage />)

    expect(screen.getByText('Loading customer records...')).toBeInTheDocument()
    pending.resolve({
      items: [],
      pagination: { page: 1, limit: 10, total: 0, total_pages: 0 },
    })
  })

  it('renders empty state when no customer records exist', async () => {
    render(<CustomersPage />)

    expect(
      await screen.findByText('No customer records yet.'),
    ).toBeInTheDocument()
    expect(screen.getByText('New submissions will appear here.')).toBeInTheDocument()
  })

  it('validates required fields and email format before submit', async () => {
    const user = userEvent.setup()
    render(<CustomersPage />)

    await user.click(await screen.findByRole('button', { name: 'Submit' }))

    expect(await screen.findByText('Name is required.')).toBeInTheDocument()
    expect(screen.getByText('Email is required.')).toBeInTheDocument()
    expect(screen.getByText('Phone is required.')).toBeInTheDocument()
    expect(screen.getByText('Request details are required.')).toBeInTheDocument()
    expect(createCustomerMock).not.toHaveBeenCalled()

    await user.type(screen.getByLabelText('Name'), 'Taylor')
    await user.type(screen.getByLabelText('Email'), 'invalid-email')
    await user.type(screen.getByLabelText('Phone'), '123')
    await user.type(screen.getByLabelText('Request Details'), 'Need help')
    await user.click(screen.getByRole('button', { name: 'Submit' }))

    expect(await screen.findByText('Enter a valid email address.')).toBeInTheDocument()
    expect(createCustomerMock).not.toHaveBeenCalled()
  })

  it('submits successfully, shows loading text, and success banner', async () => {
    const user = userEvent.setup()
    const submitDeferred = deferred<Awaited<ReturnType<typeof createCustomer>>>()
    createCustomerMock.mockReturnValueOnce(submitDeferred.promise)

    render(<CustomersPage />)

    await user.type(await screen.findByLabelText('Name'), '  Jamie Carter  ')
    await user.type(screen.getByLabelText('Email'), '  jamie@company.com  ')
    await user.type(screen.getByLabelText('Phone'), '  +44 123  ')
    await user.type(screen.getByLabelText('Request Details'), '  Need update  ')

    await user.click(screen.getByRole('button', { name: 'Submit' }))

    const submitButton = screen.getByRole('button', { name: 'Submitting...' })
    expect(submitButton).toBeDisabled()

    submitDeferred.resolve({
      id: '00000000-0000-0000-0000-000000000001',
      created_at: new Date().toISOString(),
      name: 'Jamie Carter',
      email: 'jamie@company.com',
      phone: '+44 123',
      request_details: 'Need update',
      response_data: null,
    })

    await waitFor(() => {
      expect(createCustomerMock).toHaveBeenCalledWith({
        name: 'Jamie Carter',
        email: 'jamie@company.com',
        phone: '+44 123',
        request_details: 'Need update',
        response_data: '',
      })
    })

    expect(await screen.findByRole('status')).toHaveTextContent(
      'Customer request submitted.',
    )
  })

  it('shows graceful API error message on submit failure', async () => {
    const user = userEvent.setup()
    createCustomerMock.mockRejectedValueOnce(
      new ApiError({
        status: 422,
        code: 'validation_error',
        message: 'Request validation failed',
        details: [],
      }),
    )

    render(<CustomersPage />)

    await user.type(await screen.findByLabelText('Name'), 'Jordan')
    await user.type(screen.getByLabelText('Email'), 'jordan@example.com')
    await user.type(screen.getByLabelText('Phone'), '1234')
    await user.type(screen.getByLabelText('Request Details'), 'Follow up')
    await user.click(screen.getByRole('button', { name: 'Submit' }))

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Please review the form inputs and try again.',
    )
  })

  it('resets loading state and surfaces clean list errors', async () => {
    listCustomersMock.mockRejectedValueOnce(
      new ApiError({
        status: 0,
        code: 'retry_exhausted',
        message: 'Request failed after retrying. Please try again.',
        details: { cause: 'timeout_error', attempts: 2 },
      }),
    )

    render(<CustomersPage />)

    expect(
      await screen.findByText('The request failed after retrying. Please try again shortly.'),
    ).toBeInTheDocument()
    expect(screen.queryByText('Loading customer records...')).not.toBeInTheDocument()
  })
})
