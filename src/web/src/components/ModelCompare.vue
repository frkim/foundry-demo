<script setup lang="ts">
import { computed, ref } from 'vue'
import { api } from '../api'
import type { CompareResponse, InfoResponse, ModelResult } from '../types'
import { formatLatency, formatNumber } from '../utils/format'
import { renderMarkdown } from '../utils/markdown'
import { useNativeTestId } from '../utils/test-id'

const props = defineProps<{ info: InfoResponse | null }>()

const MAX_LENGTH = 4000
const prompt = ref('Summarize in three bullet points why teams choose Microsoft Foundry for building AI agents.')
const loading = ref(false)
const error = ref<string | null>(null)
const result = ref<CompareResponse | null>(null)
const inputField = ref(null)
useNativeTestId(inputField, 'compare-input', 'textarea')

const placeholders = computed<Array<Pick<ModelResult, 'model' | 'role'>>>(() => [
  { model: props.info?.models.primary ?? 'primary model', role: 'primary' },
  { model: props.info?.models.fast ?? 'fast model', role: 'fast' },
])

const fastest = computed(() => {
  const ok = result.value?.results.filter((r) => !r.error) ?? []
  if (ok.length < 2) return null
  return ok.reduce((a, b) => (a.latency_ms <= b.latency_ms ? a : b)).model
})

async function run(): Promise<void> {
  const text = prompt.value.trim()
  if (!text || loading.value) return
  loading.value = true
  error.value = null
  result.value = null
  try {
    result.value = await api.compare(text)
  } catch (e) {
    error.value = e instanceof Error ? e.message : String(e)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div>
    <v-card elevation="1" class="mb-4">
      <v-card-item>
        <template #prepend>
          <v-avatar color="secondary" variant="tonal" rounded="lg"><v-icon icon="mdi-compare-horizontal" /></v-avatar>
        </template>
        <v-card-title>Model compare</v-card-title>
        <v-card-subtitle>
          Same prompt, two Foundry model deployments, called in parallel through the Responses API
        </v-card-subtitle>
      </v-card-item>
      <v-card-text>
        <div class="d-flex ga-3 align-start">
          <v-textarea
            ref="inputField"
            v-model="prompt"
            label="Prompt"
            rows="2"
            max-rows="6"
            auto-grow
            :maxlength="MAX_LENGTH"
            hide-details="auto"
            :disabled="loading"
            @keydown.enter.exact.prevent="run"
          />
          <v-btn
            color="primary"
            size="large"
            height="56"
            prepend-icon="mdi-play"
            data-testid="compare-btn"
            :loading="loading"
            :disabled="!prompt.trim()"
            @click="run"
          >
            Compare
          </v-btn>
        </div>
      </v-card-text>
    </v-card>

    <v-alert v-if="error" type="error" variant="tonal" class="mb-4" :text="error" data-testid="compare-error" />

    <v-row>
      <v-col v-for="(slot, index) in placeholders" :key="slot.role" cols="12" md="6">
        <v-card elevation="1" height="100%" :data-testid="`compare-result-${index}`">
          <template v-if="result?.results[index]">
            <v-card-item>
              <template #prepend>
                <v-avatar :color="slot.role === 'primary' ? 'primary' : 'accent'" variant="tonal" rounded="lg">
                  <v-icon :icon="slot.role === 'primary' ? 'mdi-brain' : 'mdi-lightning-bolt'" />
                </v-avatar>
              </template>
              <v-card-title>{{ result.results[index]!.model }}</v-card-title>
              <v-card-subtitle>{{ slot.role === 'primary' ? 'Primary (agent) model' : 'Fast model' }}</v-card-subtitle>
              <template #append>
                <v-chip v-if="fastest === result.results[index]!.model" color="success" size="small" prepend-icon="mdi-trophy">
                  Fastest
                </v-chip>
              </template>
            </v-card-item>
            <v-card-text>
              <div class="d-flex flex-wrap ga-2 mb-3">
                <v-chip size="small" prepend-icon="mdi-timer-outline" variant="tonal">
                  {{ formatLatency(result.results[index]!.latency_ms) }}
                </v-chip>
                <v-chip size="small" prepend-icon="mdi-arrow-down-bold" variant="tonal">
                  {{ formatNumber(result.results[index]!.input_tokens) }} in
                </v-chip>
                <v-chip size="small" prepend-icon="mdi-arrow-up-bold" variant="tonal">
                  {{ formatNumber(result.results[index]!.output_tokens) }} out
                </v-chip>
                <v-chip size="small" prepend-icon="mdi-counter" variant="tonal">
                  {{ formatNumber(result.results[index]!.total_tokens) }} total
                </v-chip>
              </div>
              <v-alert
                v-if="result.results[index]!.error"
                type="error"
                variant="tonal"
                density="compact"
                :text="result.results[index]!.error ?? ''"
              />
              <!-- eslint-disable-next-line vue/no-v-html -- sanitized with DOMPurify -->
              <div v-else class="fg-markdown" v-html="renderMarkdown(result.results[index]!.output)" />
            </v-card-text>
          </template>
          <template v-else>
            <v-card-item>
              <v-card-title>{{ slot.model }}</v-card-title>
              <v-card-subtitle>{{ slot.role === 'primary' ? 'Primary (agent) model' : 'Fast model' }}</v-card-subtitle>
            </v-card-item>
            <v-card-text>
              <v-skeleton-loader v-if="loading" type="paragraph, paragraph" />
              <div v-else class="text-medium-emphasis text-body-2">Run a comparison to see this model's answer.</div>
            </v-card-text>
          </template>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>
