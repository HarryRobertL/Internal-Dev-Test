import { useCallback, useEffect, useRef, useState } from 'react'

import { ApiError, createCustomer, listCustomers } from '../api/customers'
import { CustomerForm } from '../components/CustomerForm'
import { CustomerTable } from '../components/CustomerTable'
import { PageShell } from '../components/PageShell'
import type {
  Customer,
  CustomerCreateInput,
  PaginationMeta,
} from '../types/customer'

const PAGE_LIMIT = 10

const initialPagination: PaginationMeta = {
  page: 1,
  limit: PAGE_LIMIT,
  total: 0,
  total_pages: 0,
}

function toUserMessage(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.code === 'validation_error') {
      return 'Please review the form inputs and try again.'
    }
    if (error.code === 'not_found') {
      return 'The requested customer record was not found.'
    }
    if (error.code === 'timeout_error') {
      return 'The API took too long to respond. Please retry.'
    }
    if (error.code === 'retry_exhausted') {
      return 'The request failed after retrying. Please try again shortly.'
    }
    return error.message
  }
  return 'Something went wrong. Please try again.'
}

export function CustomersPage() {
  const [customers, setCustomers] = useState<Customer[]>([])
  const [pagination, setPagination] = useState<PaginationMeta>(initialPagination)
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [loadError, setLoadError] = useState<string | null>(null)

  const [isSubmitting, setIsSubmitting] = useState<boolean>(false)
  const [submitError, setSubmitError] = useState<string | null>(null)
  const [submitSuccess, setSubmitSuccess] = useState<string | null>(null)
  const listRequestIdRef = useRef(0)

  const fetchCustomers = useCallback(async (page: number) => {
    const requestId = ++listRequestIdRef.current
    setIsLoading(true)
    setLoadError(null)

    try {
      const data = await listCustomers({ page, limit: PAGE_LIMIT })
      if (requestId !== listRequestIdRef.current) return
      setCustomers(data.items)
      setPagination(data.pagination)
    } catch (error) {
      if (requestId !== listRequestIdRef.current) return
      if (error instanceof ApiError && error.code === 'network_error') {
        setLoadError('Unable to reach the API. Please retry.')
        return
      }
      setLoadError(toUserMessage(error))
    } finally {
      if (requestId === listRequestIdRef.current) {
        setIsLoading(false)
      }
    }
  }, [])

  useEffect(() => {
    void fetchCustomers(pagination.page)
  }, [fetchCustomers, pagination.page])

  useEffect(() => {
    return () => {
      // Invalidate pending async list responses when component unmounts.
      listRequestIdRef.current += 1
    }
  }, [])

  async function handleSubmit(payload: CustomerCreateInput): Promise<boolean> {
    setIsSubmitting(true)
    setSubmitError(null)
    setSubmitSuccess(null)

    try {
      await createCustomer(payload)
      setSubmitSuccess('Customer request submitted.')
      if (pagination.page === 1) {
        await fetchCustomers(1)
      } else {
        setPagination((prev) => ({ ...prev, page: 1 }))
      }
      return true
    } catch (error) {
      setSubmitError(toUserMessage(error))
      return false
    } finally {
      setIsSubmitting(false)
    }
  }

  function handlePageChange(nextPage: number) {
    if (nextPage < 1 || nextPage === pagination.page) return
    setPagination((prev) => ({ ...prev, page: nextPage }))
  }

  function handleRetryLoad() {
    void fetchCustomers(pagination.page)
  }

  return (
    <PageShell>
      <div className="grid grid-cols-1 gap-7 lg:grid-cols-5">
        <div className="lg:col-span-2">
          <CustomerForm
            isSubmitting={isSubmitting}
            submitError={submitError}
            submitSuccess={submitSuccess}
            onSubmit={handleSubmit}
          />
        </div>

        <div className="lg:col-span-3">
          <CustomerTable
            customers={customers}
            pagination={pagination}
            isLoading={isLoading}
            loadError={loadError}
            onPageChange={handlePageChange}
            onRetry={handleRetryLoad}
          />
        </div>
      </div>
    </PageShell>
  )
}
