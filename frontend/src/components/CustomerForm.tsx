import { useState } from 'react'
import type { FormEvent } from 'react'

import type { CustomerCreateInput } from '../types/customer'

type FieldErrors = Partial<Record<keyof CustomerCreateInput, string>>

interface CustomerFormProps {
  isSubmitting: boolean
  submitError: string | null
  submitSuccess: string | null
  onSubmit: (payload: CustomerCreateInput) => Promise<boolean>
}

const initialState: CustomerCreateInput = {
  name: '',
  email: '',
  phone: '',
  request_details: '',
  response_data: '',
}

const fieldId = {
  name: 'customer-name',
  email: 'customer-email',
  phone: 'customer-phone',
  request_details: 'customer-request-details',
  response_data: 'customer-response-data',
} as const

function isValidEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}

function trimPayload(payload: CustomerCreateInput): CustomerCreateInput {
  return {
    name: payload.name.trim(),
    email: payload.email.trim(),
    phone: payload.phone.trim(),
    request_details: payload.request_details.trim(),
    response_data: payload.response_data?.trim(),
  }
}

function validate(payload: CustomerCreateInput): FieldErrors {
  const errors: FieldErrors = {}

  if (!payload.name) errors.name = 'Name is required.'
  if (!payload.email) errors.email = 'Email is required.'
  if (payload.email && !isValidEmail(payload.email)) {
    errors.email = 'Enter a valid email address.'
  }
  if (!payload.phone) errors.phone = 'Phone is required.'
  if (!payload.request_details) {
    errors.request_details = 'Request details are required.'
  }

  return errors
}

export function CustomerForm({
  isSubmitting,
  submitError,
  submitSuccess,
  onSubmit,
}: CustomerFormProps) {
  const [form, setForm] = useState<CustomerCreateInput>(initialState)
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({})

  function update<K extends keyof CustomerCreateInput>(key: K, value: string) {
    setForm((prev) => ({ ...prev, [key]: value }))
    setFieldErrors((prev) => ({ ...prev, [key]: undefined }))
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    const normalized = trimPayload(form)
    const errors = validate(normalized)
    setFieldErrors(errors)

    if (Object.keys(errors).length > 0) return

    const isSuccess = await onSubmit(normalized)
    if (isSuccess) {
      setForm(initialState)
      setFieldErrors({})
    }
  }

  return (
    <section className="app-card w-full max-w-xl rounded-xl p-6">
      <h2 className="mb-1 text-xl font-semibold tracking-tight text-slate-900">Submit Request</h2>
      <p className="text-muted-foreground mb-6 text-sm leading-6">
        Enter customer details and submit to create a new request record.
      </p>

      {submitSuccess ? (
        <div
          role="status"
          className="mb-4 rounded-lg border border-emerald-200 bg-emerald-50 px-3.5 py-2.5 text-sm text-emerald-800"
        >
          {submitSuccess}
        </div>
      ) : null}
      {submitError ? (
        <div
          role="alert"
          className="mb-4 rounded-lg border border-red-200 bg-red-50 px-3.5 py-2.5 text-sm text-red-700"
        >
          {submitError}
        </div>
      ) : null}

      <form className="space-y-5" onSubmit={handleSubmit} noValidate>
        <div className="space-y-1.5">
          <label
            htmlFor={fieldId.name}
            className="block text-sm font-medium text-slate-700"
          >
            Name
          </label>
          <input
            id={fieldId.name}
            className="h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-sm text-slate-900 shadow-sm transition-colors duration-150 placeholder:text-slate-400 hover:border-slate-400 focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-200"
            value={form.name}
            onChange={(event) => update('name', event.target.value)}
            disabled={isSubmitting}
            placeholder="e.g. Jamie Carter"
            aria-invalid={Boolean(fieldErrors.name)}
          />
          {fieldErrors.name ? (
            <p className="text-xs text-red-600">{fieldErrors.name}</p>
          ) : null}
        </div>

        <div className="space-y-1.5">
          <label
            htmlFor={fieldId.email}
            className="block text-sm font-medium text-slate-700"
          >
            Email
          </label>
          <input
            id={fieldId.email}
            className="h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-sm text-slate-900 shadow-sm transition-colors duration-150 placeholder:text-slate-400 hover:border-slate-400 focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-200"
            value={form.email}
            onChange={(event) => update('email', event.target.value)}
            disabled={isSubmitting}
            placeholder="name@company.com"
            aria-invalid={Boolean(fieldErrors.email)}
          />
          {fieldErrors.email ? (
            <p className="text-xs text-red-600">{fieldErrors.email}</p>
          ) : null}
        </div>

        <div className="space-y-1.5">
          <label
            htmlFor={fieldId.phone}
            className="block text-sm font-medium text-slate-700"
          >
            Phone
          </label>
          <input
            id={fieldId.phone}
            className="h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-sm text-slate-900 shadow-sm transition-colors duration-150 placeholder:text-slate-400 hover:border-slate-400 focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-200"
            value={form.phone}
            onChange={(event) => update('phone', event.target.value)}
            disabled={isSubmitting}
            placeholder="+44 20 7946 0958"
            aria-invalid={Boolean(fieldErrors.phone)}
          />
          {fieldErrors.phone ? (
            <p className="text-xs text-red-600">{fieldErrors.phone}</p>
          ) : null}
        </div>

        <div className="space-y-1.5">
          <label
            htmlFor={fieldId.request_details}
            className="block text-sm font-medium text-slate-700"
          >
            Request Details
          </label>
          <textarea
            id={fieldId.request_details}
            className="min-h-28 w-full rounded-md border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 shadow-sm transition-colors duration-150 placeholder:text-slate-400 hover:border-slate-400 focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-200"
            value={form.request_details}
            onChange={(event) => update('request_details', event.target.value)}
            disabled={isSubmitting}
            placeholder="Describe the customer request..."
            aria-invalid={Boolean(fieldErrors.request_details)}
          />
          {fieldErrors.request_details ? (
            <p className="text-xs text-red-600">{fieldErrors.request_details}</p>
          ) : null}
        </div>

        <div className="space-y-1.5">
          <label
            htmlFor={fieldId.response_data}
            className="block text-sm font-medium text-slate-700"
          >
            Response Data (optional)
          </label>
          <textarea
            id={fieldId.response_data}
            className="min-h-20 w-full rounded-md border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 shadow-sm transition-colors duration-150 placeholder:text-slate-400 hover:border-slate-400 focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-200"
            value={form.response_data}
            onChange={(event) => update('response_data', event.target.value)}
            disabled={isSubmitting}
            placeholder="Optional metadata or response context"
          />
        </div>

        <button
          type="submit"
          disabled={isSubmitting}
          className="inline-flex items-center justify-center rounded-md bg-black px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-colors transition-transform duration-150 hover:bg-black/90 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50"
          aria-busy={isSubmitting}
        >
          {isSubmitting ? 'Submitting...' : 'Submit'}
        </button>
      </form>
    </section>
  )
}
