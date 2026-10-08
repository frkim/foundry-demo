import type { ToolCall } from '../types'

export function formatNumber(value: number | null | undefined): string {
  return value === null || value === undefined ? '—' : value.toLocaleString()
}

export function formatLatency(ms: number | null | undefined): string {
  if (ms === null || ms === undefined) return '—'
  return ms >= 1000 ? `${(ms / 1000).toFixed(2)} s` : `${ms} ms`
}

export function formatTime(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    month: 'short',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

export function toolLabel(call: ToolCall): string {
  switch (call.type) {
    case 'mcp_call':
      return ['MCP', call.server_label, call.name].filter(Boolean).join(' · ')
    case 'mcp_list_tools':
      return ['MCP', call.server_label, 'list tools'].filter(Boolean).join(' · ')
    case 'code_interpreter_call':
      return 'Code Interpreter'
    case 'web_search_call':
      return 'Web search'
    case 'file_search_call':
      return 'File search'
    default:
      return call.name ? `${call.type} · ${call.name}` : call.type
  }
}

export function toolIcon(call: ToolCall): string {
  if (call.type.startsWith('mcp')) return 'mdi-connection'
  if (call.type === 'code_interpreter_call') return 'mdi-language-python'
  if (call.type.includes('search')) return 'mdi-magnify'
  return 'mdi-tools'
}

export function newId(): string {
  return typeof crypto !== 'undefined' && 'randomUUID' in crypto
    ? crypto.randomUUID()
    : `${Date.now()}-${Math.random().toString(16).slice(2)}`
}
