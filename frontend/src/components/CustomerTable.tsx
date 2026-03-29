import type { Customer, PaginationMeta } from '../types/customer'

interface CustomerTableProps {
  customers: Customer[]
  pagination: PaginationMeta
  isLoading: boolean
  loadError: string | null
  onPageChange: (page: number) => void
  onRetry?: () => void
}

function formatDate(value: string): string {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString()
}

export function CustomerTable({
  customers,
  pagination,
  isLoading,
  loadError,
  onPageChange,
  onRetry,
}: CustomerTableProps) {
  const canGoPrevious = pagination.page > 1
  const canGoNext = pagination.page < pagination.total_pages

  return (
    <section className="app-card rounded-xl p-6 md:p-7">
      <div className="mb-5 flex items-center justify-between">
        <h2 className="text-xl font-semibold text-slate-900">Customer Requests</h2>
        <p className="text-sm font-medium text-slate-500">Total records: {pagination.total}</p>
      </div>

      {isLoading ? (
        <div className="rounded-lg border border-slate-200 bg-slate-50 px-4 py-6 text-sm text-slate-600">
          Loading customer records...
        </div>
      ) : null}
      {loadError ? (
        <div
          role="alert"
          className="flex items-center justify-between gap-3 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
        >
          <span>{loadError}</span>
          {onRetry ? (
            <button
              className="rounded-md border border-red-300 bg-white px-2.5 py-1 text-xs font-semibold text-red-700 transition-colors duration-150 hover:bg-red-100 active:bg-red-200 disabled:cursor-not-allowed disabled:opacity-60"
              onClick={onRetry}
            >
              Retry
            </button>
          ) : null}
        </div>
      ) : null}
      {!isLoading && !loadError && customers.length === 0 ? (
        <div className="rounded-lg border border-dashed border-slate-300 bg-slate-50 px-4 py-8 text-center">
          <p className="text-sm font-medium text-slate-700">No customer records yet.</p>
          <p className="mt-1 text-sm text-slate-500">
            New submissions will appear here.
          </p>
        </div>
      ) : null}

      {!isLoading && !loadError && customers.length > 0 ? (
        <div className="overflow-x-auto rounded-lg border border-slate-200">
          <table className="min-w-full border-collapse text-left text-sm">
            <thead className="bg-slate-50">
              <tr className="border-b border-slate-200 text-slate-600">
                <th className="px-3 py-2.5 text-[13px] font-semibold tracking-wide">Created</th>
                <th className="px-3 py-2.5 text-[13px] font-semibold tracking-wide">Name</th>
                <th className="px-3 py-2.5 text-[13px] font-semibold tracking-wide">Email</th>
                <th className="px-3 py-2.5 text-[13px] font-semibold tracking-wide">Phone</th>
                <th className="px-3 py-2.5 text-[13px] font-semibold tracking-wide">
                  Request Details
                </th>
              </tr>
            </thead>
            <tbody>
              {customers.map((customer) => (
                <tr
                  key={customer.id}
                  className="border-b border-slate-100 transition-colors duration-150 hover:bg-slate-50"
                >
                  <td className="px-3 py-2.5 text-slate-600">
                    {formatDate(customer.created_at)}
                  </td>
                  <td className="px-3 py-2.5 text-slate-800">{customer.name}</td>
                  <td className="px-3 py-2.5 text-slate-800">{customer.email}</td>
                  <td className="px-3 py-2.5 text-slate-800">{customer.phone}</td>
                  <td className="px-3 py-2.5 text-slate-700 whitespace-pre-line break-words">
                    {customer.request_details}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}

      <div className="mt-5 flex flex-wrap items-center justify-between gap-2">
        <span className="text-sm text-slate-500">
          Showing page {pagination.page} of {Math.max(1, pagination.total_pages)}
        </span>
        <button
          className="rounded-md border border-slate-300 bg-white px-3 py-1.5 text-sm font-semibold text-slate-700 shadow-sm transition-all duration-150 hover:-translate-y-px hover:bg-slate-50 active:translate-y-0 active:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-50"
          onClick={() => onPageChange(pagination.page - 1)}
          disabled={!canGoPrevious || isLoading}
        >
          Previous
        </button>
        <button
          className="rounded-md border border-slate-300 bg-white px-3 py-1.5 text-sm font-semibold text-slate-700 shadow-sm transition-all duration-150 hover:-translate-y-px hover:bg-slate-50 active:translate-y-0 active:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-50"
          onClick={() => onPageChange(pagination.page + 1)}
          disabled={!canGoNext || isLoading}
        >
          Next
        </button>
      </div>
    </section>
  )
}
