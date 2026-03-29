export interface Customer {
  id: string
  created_at: string
  name: string
  email: string
  phone: string
  request_details: string
  response_data: string | null
}

export interface PaginationMeta {
  page: number
  limit: number
  total: number
  total_pages: number
}

export interface CustomerListData {
  items: Customer[]
  pagination: PaginationMeta
}

export interface CustomerCreateInput {
  name: string
  email: string
  phone: string
  request_details: string
  response_data?: string
}

export interface ApiErrorInfo {
  code: string
  message: string
  details: unknown
}

export interface ApiMeta {
  pagination: PaginationMeta | null
}

export interface ApiEnvelope<TData, TMeta = ApiMeta | null> {
  data: TData | null
  error: ApiErrorInfo | null
  meta: TMeta
}
