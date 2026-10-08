import type { ChatResponse, CompareResponse, HistoryResponse, InfoResponse } from './types'

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
    readonly correlationId?: string,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

interface ErrorPayload {
  error?: { message?: string; correlation_id?: string }
  detail?: string | Array<{ msg?: string; loc?: Array<string | number> }>
}

function messageFrom(payload: ErrorPayload | null, status: number): string {
  if (payload?.error?.message) return payload.error.message
  const detail = payload?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail.length > 0) {
    const first = detail[0]
    const field = first?.loc?.slice(1).join('.')
    return field ? `${field}: ${first?.msg ?? 'invalid value'}` : (first?.msg ?? 'Invalid request')
  }
  return `Request failed (HTTP ${status})`
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response
  try {
    response = await fetch(path, {
      ...init,
      headers: { Accept: 'application/json', 'Content-Type': 'application/json', ...init?.headers },
    })
  } catch {
    throw new ApiError('Network error: the API is unreachable.', 0)
  }
  const payload: unknown = await response.json().catch(() => null)
  if (!response.ok) {
    const errorPayload = payload as ErrorPayload | null
    throw new ApiError(messageFrom(errorPayload, response.status), response.status, errorPayload?.error?.correlation_id)
  }
  return payload as T
}

export const api = {
  info: () => request<InfoResponse>('/api/info'),
  chat: (message: string, conversationId?: string | null) =>
    request<ChatResponse>('/api/agent/chat', {
      method: 'POST',
      body: JSON.stringify({ message, conversation_id: conversationId ?? null }),
    }),
  compare: (prompt: string) =>
    request<CompareResponse>('/api/models/compare', { method: 'POST', body: JSON.stringify({ prompt }) }),
  history: () => request<HistoryResponse>('/api/history'),
}
