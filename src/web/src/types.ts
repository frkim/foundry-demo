export interface ToolCall {
  type: string
  name: string | null
  server_label: string | null
  status: string | null
}

export interface Usage {
  input_tokens: number | null
  output_tokens: number | null
  total_tokens: number | null
}

export interface Citation {
  url: string
  title: string | null
}

export interface GeneratedFile {
  container_id: string
  file_id: string
  filename: string
  url: string
}

export interface ChatResponse {
  text: string
  conversation_id: string
  response_id: string | null
  agent_name: string
  agent_version: string | null
  tool_calls: ToolCall[]
  citations: Citation[]
  files: GeneratedFile[]
  usage: Usage
  latency_ms: number
}

export interface ModelResult {
  model: string
  role: 'primary' | 'fast'
  output: string
  latency_ms: number
  input_tokens: number | null
  output_tokens: number | null
  total_tokens: number | null
  error: string | null
}

export interface CompareResponse {
  prompt: string
  results: ModelResult[]
}

export type RunKind = 'agent' | 'compare'

export interface RunRecord {
  id: string
  timestamp: string
  kind: RunKind
  target: string
  prompt_preview: string
  latency_ms: number
  input_tokens: number | null
  output_tokens: number | null
  total_tokens: number | null
  tool_calls: number
  status: 'ok' | 'error'
  error: string | null
}

export interface HistoryResponse {
  items: RunRecord[]
  count: number
  capacity: number
}

export interface InfoResponse {
  app_name: string
  app_version: string
  region: string
  endpoint_host: string | null
  project_name: string | null
  configured: boolean
  telemetry_enabled: boolean
  models: { primary: string; fast: string }
  agent: {
    name: string
    version: string | null
    status: string
    error: string | null
    tools: string[]
  }
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'error'
  text: string
  toolCalls?: ToolCall[]
  citations?: Citation[]
  files?: GeneratedFile[]
  usage?: Usage
  latencyMs?: number
  agentVersion?: string | null
}
