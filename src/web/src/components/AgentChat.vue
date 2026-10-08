<script setup lang="ts">
import { computed, nextTick, ref } from 'vue'
import { api } from '../api'
import type { ChatMessage, InfoResponse } from '../types'
import { formatLatency, formatNumber, newId, toolIcon, toolLabel } from '../utils/format'
import { renderMarkdown, unreferencedFiles } from '../utils/markdown'
import { useNativeTestId } from '../utils/test-id'
import FoundryLogo from './FoundryLogo.vue'

const props = defineProps<{ info: InfoResponse | null }>()

const MAX_LENGTH = 4000
const suggestions = [
  'What is the difference between prompt agents and hosted agents in Microsoft Foundry Agent Service? Cite Microsoft Learn.',
  'Use Code Interpreter: 2,000 conversations/day, 1,500 input + 500 output tokens each, at $0.40/$1.60 per 1M tokens. Calculate daily, 30-day and 365-day cost; show a table and a bar chart.',
  'In Microsoft Foundry, what is the difference between a Foundry resource and a Foundry project? Which one owns networking and model deployments?',
]

const messages = ref<ChatMessage[]>([])
const input = ref('')
const loading = ref(false)
const conversationId = ref<string | null>(null)
const scroller = ref<HTMLElement | null>(null)
const inputField = ref(null)
useNativeTestId(inputField, 'prompt-input', 'textarea')

const canSend = computed(() => input.value.trim().length > 0 && input.value.length <= MAX_LENGTH && !loading.value)
const agentLabel = computed(() => {
  const agent = props.info?.agent
  if (!agent) return 'foundry-guide'
  return agent.version ? `${agent.name} v${agent.version}` : agent.name
})

async function scrollToBottom(): Promise<void> {
  await nextTick()
  scroller.value?.scrollTo({ top: scroller.value.scrollHeight, behavior: 'smooth' })
}

function useSuggestion(text: string): void {
  input.value = text
}

async function send(): Promise<void> {
  const text = input.value.trim()
  if (!text || loading.value || text.length > MAX_LENGTH) return
  messages.value.push({ id: newId(), role: 'user', text })
  input.value = ''
  loading.value = true
  void scrollToBottom()
  try {
    const result = await api.chat(text, conversationId.value)
    conversationId.value = result.conversation_id
    messages.value.push({
      id: result.response_id ?? newId(),
      role: 'assistant',
      text: result.text || '_The agent returned no text._',
      toolCalls: result.tool_calls,
      citations: result.citations,
      files: result.files,
      usage: result.usage,
      latencyMs: result.latency_ms,
      agentVersion: result.agent_version,
    })
  } catch (error) {
    messages.value.push({ id: newId(), role: 'error', text: error instanceof Error ? error.message : String(error) })
  } finally {
    loading.value = false
    void scrollToBottom()
  }
}

function onKeydown(event: KeyboardEvent): void {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    void send()
  }
}

function newConversation(): void {
  messages.value = []
  conversationId.value = null
  input.value = ''
}

function isImage(filename: string): boolean {
  return /\.(png|jpe?g|gif|webp|svg)$/i.test(filename)
}
</script>

<template>
  <v-card elevation="1" class="d-flex flex-column" style="min-height: calc(100vh - 260px)">
    <v-card-item>
      <template #prepend>
        <v-avatar color="primary" variant="tonal" rounded="lg">
          <v-icon icon="mdi-robot-happy-outline" />
        </v-avatar>
      </template>
      <v-card-title>Agent chat</v-card-title>
      <v-card-subtitle>
        {{ agentLabel }} · Microsoft Learn MCP + Code Interpreter · Responses API
        <span v-if="conversationId" class="ml-1">· conversation {{ conversationId.slice(0, 18) }}…</span>
      </v-card-subtitle>
      <template #append>
        <v-btn
          variant="tonal"
          color="primary"
          prepend-icon="mdi-plus"
          data-testid="new-conversation-btn"
          :disabled="loading"
          @click="newConversation"
        >
          New conversation
        </v-btn>
      </template>
    </v-card-item>
    <v-progress-linear :active="loading" indeterminate color="primary" height="3" />
    <v-divider />

    <div ref="scroller" class="fg-scroll flex-grow-1 pa-4" style="max-height: calc(100vh - 430px); min-height: 280px">
      <div v-if="messages.length === 0" class="text-center py-8">
        <FoundryLogo :size="64" />
        <div class="text-h5 mt-4 font-weight-bold fg-gradient-text">Ask Foundry Guide</div>
        <div class="text-body-2 text-medium-emphasis mt-2 mx-auto" style="max-width: 560px">
          A Microsoft Foundry prompt agent grounded in Microsoft Learn through the MCP server, with a Code Interpreter
          sandbox for calculations and charts. Pick a suggestion below or type your own question.
        </div>
      </div>

      <div v-for="message in messages" :key="message.id" class="mb-4">
        <div v-if="message.role === 'user'" class="d-flex justify-end">
          <v-card class="fg-bubble-user px-4 py-3" max-width="80%" elevation="0" data-testid="user-message">
            <div style="white-space: pre-wrap">{{ message.text }}</div>
          </v-card>
        </div>

        <v-alert
          v-else-if="message.role === 'error'"
          type="error"
          variant="tonal"
          density="compact"
          data-testid="error-message"
          :text="message.text"
        />

        <div v-else class="d-flex ga-3" data-testid="assistant-message">
          <div class="pt-1"><FoundryLogo :size="32" /></div>
          <v-card variant="flat" color="surface-variant" class="px-4 py-3 flex-grow-1" style="min-width: 0">
            <div v-if="message.toolCalls?.length" class="d-flex flex-wrap ga-2 mb-3" data-testid="tool-calls">
              <v-chip
                v-for="(call, index) in message.toolCalls"
                :key="index"
                size="small"
                :color="call.type === 'code_interpreter_call' ? 'accent' : 'primary'"
                variant="tonal"
                :prepend-icon="toolIcon(call)"
                data-testid="tool-call-chip"
              >
                {{ toolLabel(call) }}
              </v-chip>
            </div>
            <!-- eslint-disable-next-line vue/no-v-html -- sanitized with DOMPurify -->
            <div class="fg-markdown text-body-1" v-html="renderMarkdown(message.text, message.files)" />
            <div v-if="unreferencedFiles(message.text, message.files).length" class="d-flex flex-wrap ga-3 mt-3">
              <template v-for="file in unreferencedFiles(message.text, message.files)" :key="file.file_id">
                <a v-if="isImage(file.filename)" :href="file.url" target="_blank" rel="noopener">
                  <img :src="file.url" :alt="file.filename" style="max-width: 100%; max-height: 360px; border-radius: 8px" />
                </a>
                <v-chip v-else :href="file.url" prepend-icon="mdi-download" size="small" variant="outlined">
                  {{ file.filename }}
                </v-chip>
              </template>
            </div>
            <div v-if="message.citations?.length" class="mt-3 d-flex flex-wrap ga-2">
              <v-chip
                v-for="citation in message.citations"
                :key="citation.url"
                :href="citation.url"
                target="_blank"
                rel="noopener"
                size="x-small"
                variant="outlined"
                prepend-icon="mdi-book-open-page-variant-outline"
              >
                {{ citation.title || citation.url }}
              </v-chip>
            </div>
            <div class="text-caption text-medium-emphasis mt-3" data-testid="message-meta">
              <v-icon size="14" icon="mdi-timer-outline" /> {{ formatLatency(message.latencyMs) }}
              <span class="mx-1">·</span>
              <v-icon size="14" icon="mdi-counter" /> {{ formatNumber(message.usage?.total_tokens) }} tokens
              ({{ formatNumber(message.usage?.input_tokens) }} in / {{ formatNumber(message.usage?.output_tokens) }}
              out)
              <span v-if="message.agentVersion" class="mx-1">· agent v{{ message.agentVersion }}</span>
            </div>
          </v-card>
        </div>
      </div>

      <div v-if="loading" class="d-flex ga-3 align-center" data-testid="thinking-indicator">
        <FoundryLogo :size="32" />
        <v-card variant="flat" color="surface-variant" class="px-4 py-3">
          <span class="fg-dot" /><span class="fg-dot" /><span class="fg-dot" />
          <span class="text-caption text-medium-emphasis ml-2">The agent is thinking and may call tools…</span>
        </v-card>
      </div>
    </div>

    <v-divider />
    <div class="pa-4">
      <div class="d-flex flex-wrap ga-2 mb-3">
        <v-chip
          v-for="(suggestion, index) in suggestions"
          :key="suggestion"
          :data-testid="`suggestion-${index}`"
          prepend-icon="mdi-lightbulb-on-outline"
          variant="outlined"
          color="primary"
          size="small"
          :disabled="loading"
          @click="useSuggestion(suggestion)"
        >
          {{ suggestion }}
        </v-chip>
      </div>
      <div class="d-flex ga-3 align-start">
        <v-textarea
          ref="inputField"
          v-model="input"
          label="Ask about Microsoft Foundry…"
          placeholder="Press Enter to send, Shift+Enter for a new line"
          rows="1"
          max-rows="6"
          auto-grow
          :counter="MAX_LENGTH"
          :maxlength="MAX_LENGTH"
          persistent-counter
          hide-details="auto"
          :disabled="loading"
          @keydown="onKeydown"
        />
        <v-btn
          color="primary"
          size="large"
          height="48"
          append-icon="mdi-send"
          data-testid="send-btn"
          :loading="loading"
          :disabled="!canSend"
          @click="send"
        >
          Send
        </v-btn>
      </div>
    </div>
  </v-card>
</template>
