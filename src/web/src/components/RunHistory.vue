<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { api } from '../api'
import type { RunRecord } from '../types'
import { formatLatency, formatNumber, formatTime } from '../utils/format'

const props = defineProps<{ active: boolean }>()

const items = ref<RunRecord[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
const search = ref('')
const kind = ref<'all' | 'agent' | 'compare'>('all')
const status = ref<'all' | 'ok' | 'error'>('all')

const headers = [
  { title: 'Time', key: 'timestamp', sortable: true },
  { title: 'Kind', key: 'kind', sortable: true },
  { title: 'Agent / model', key: 'target', sortable: true },
  { title: 'Prompt', key: 'prompt_preview', sortable: false },
  { title: 'Latency', key: 'latency_ms', sortable: true, align: 'end' as const },
  { title: 'Tokens in', key: 'input_tokens', sortable: true, align: 'end' as const },
  { title: 'Tokens out', key: 'output_tokens', sortable: true, align: 'end' as const },
  { title: 'Tools', key: 'tool_calls', sortable: true, align: 'end' as const },
  { title: 'Status', key: 'status', sortable: true },
]

const kindOptions = [
  { title: 'All kinds', value: 'all' },
  { title: 'Agent', value: 'agent' },
  { title: 'Model compare', value: 'compare' },
]
const statusOptions = [
  { title: 'All statuses', value: 'all' },
  { title: 'Succeeded', value: 'ok' },
  { title: 'Failed', value: 'error' },
]

const filtered = computed(() =>
  items.value.filter(
    (item) => (kind.value === 'all' || item.kind === kind.value) && (status.value === 'all' || item.status === status.value),
  ),
)

async function refresh(): Promise<void> {
  loading.value = true
  try {
    items.value = (await api.history()).items
    error.value = null
  } catch (e) {
    error.value = e instanceof Error ? e.message : String(e)
  } finally {
    loading.value = false
  }
}

watch(
  () => props.active,
  (isActive) => {
    if (isActive) void refresh()
  },
  { immediate: true },
)
</script>

<template>
  <v-card elevation="1">
    <v-card-item>
      <template #prepend>
        <v-avatar color="primary" variant="tonal" rounded="lg"><v-icon icon="mdi-history" /></v-avatar>
      </template>
      <v-card-title>Run history</v-card-title>
      <v-card-subtitle>Last 200 agent and model runs served by this instance (in memory)</v-card-subtitle>
      <template #append>
        <v-btn variant="tonal" prepend-icon="mdi-refresh" :loading="loading" data-testid="history-refresh" @click="refresh">
          Refresh
        </v-btn>
      </template>
    </v-card-item>
    <v-card-text>
      <v-row dense class="mb-2">
        <v-col cols="12" md="6">
          <v-text-field
            v-model="search"
            label="Search"
            prepend-inner-icon="mdi-magnify"
            clearable
            hide-details
            data-testid="history-search"
          />
        </v-col>
        <v-col cols="6" md="3">
          <v-select v-model="kind" :items="kindOptions" label="Kind" hide-details data-testid="history-kind-filter" />
        </v-col>
        <v-col cols="6" md="3">
          <v-select v-model="status" :items="statusOptions" label="Status" hide-details data-testid="history-status-filter" />
        </v-col>
      </v-row>
      <v-alert v-if="error" type="error" variant="tonal" density="compact" class="mb-2" :text="error" />
      <v-data-table
        :headers="headers"
        :items="filtered"
        :search="search ?? ''"
        :loading="loading"
        :sort-by="[{ key: 'timestamp', order: 'desc' }]"
        :items-per-page="10"
        :items-per-page-options="[5, 10, 25, 50, 100]"
        item-value="id"
        hover
        density="comfortable"
        data-testid="history-table"
        no-data-text="No runs yet - chat with the agent or compare models."
      >
        <template #[`item.timestamp`]="{ item }">{{ formatTime(item.timestamp) }}</template>
        <template #[`item.kind`]="{ item }">
          <v-chip
            size="small"
            variant="tonal"
            :color="item.kind === 'agent' ? 'primary' : 'secondary'"
            :prepend-icon="item.kind === 'agent' ? 'mdi-robot-outline' : 'mdi-compare-horizontal'"
          >
            {{ item.kind === 'agent' ? 'Agent' : 'Compare' }}
          </v-chip>
        </template>
        <template #[`item.prompt_preview`]="{ item }">
          <span class="d-inline-block text-truncate" style="max-width: 320px" :title="item.prompt_preview">
            {{ item.prompt_preview }}
          </span>
        </template>
        <template #[`item.latency_ms`]="{ item }">{{ formatLatency(item.latency_ms) }}</template>
        <template #[`item.input_tokens`]="{ item }">{{ formatNumber(item.input_tokens) }}</template>
        <template #[`item.output_tokens`]="{ item }">{{ formatNumber(item.output_tokens) }}</template>
        <template #[`item.status`]="{ item }">
          <v-chip
            size="small"
            variant="tonal"
            :color="item.status === 'ok' ? 'success' : 'error'"
            :prepend-icon="item.status === 'ok' ? 'mdi-check' : 'mdi-alert'"
          >
            {{ item.status === 'ok' ? 'OK' : 'Error' }}
            <v-tooltip v-if="item.error" activator="parent" location="top" max-width="400">{{ item.error }}</v-tooltip>
          </v-chip>
        </template>
      </v-data-table>
    </v-card-text>
  </v-card>
</template>
