<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useTheme } from 'vuetify'
import { api } from './api'
import AboutPanel from './components/AboutPanel.vue'
import AgentChat from './components/AgentChat.vue'
import FoundryLogo from './components/FoundryLogo.vue'
import ModelCompare from './components/ModelCompare.vue'
import RunHistory from './components/RunHistory.vue'
import { THEME_STORAGE_KEY } from './plugins/vuetify'
import type { InfoResponse } from './types'

type TabKey = 'agent' | 'compare' | 'history' | 'about'

const theme = useTheme()
const tab = ref<TabKey>('agent')
const info = ref<InfoResponse | null>(null)
const infoError = ref<string | null>(null)
let infoTimer: number | undefined

const isDark = computed(() => theme.global.current.value.dark)

function toggleTheme(): void {
  const next = isDark.value ? 'foundryLight' : 'foundryDark'
  theme.change(next)
  window.localStorage.setItem(THEME_STORAGE_KEY, next)
}

async function loadInfo(): Promise<void> {
  try {
    info.value = await api.info()
    infoError.value = null
  } catch (error) {
    infoError.value = error instanceof Error ? error.message : String(error)
  }
  window.clearTimeout(infoTimer)
  // Poll until the agent is ready so the status chip and footer update after start-up.
  if (info.value?.agent.status !== 'ready') infoTimer = window.setTimeout(loadInfo, 10000)
}

const agentStatus = computed(() => {
  const status = info.value?.agent.status ?? 'unknown'
  const map: Record<string, { color: string; icon: string; label: string }> = {
    ready: { color: 'success', icon: 'mdi-check-circle', label: 'Agent ready' },
    creating: { color: 'warning', icon: 'mdi-progress-clock', label: 'Agent starting' },
    pending: { color: 'warning', icon: 'mdi-progress-clock', label: 'Agent starting' },
    error: { color: 'error', icon: 'mdi-alert-circle', label: 'Agent error' },
    not_configured: { color: 'grey', icon: 'mdi-cog-off', label: 'Not configured' },
  }
  return map[status] ?? { color: 'grey', icon: 'mdi-help-circle', label: 'Status unknown' }
})

const tabs: Array<{ value: TabKey; label: string; icon: string }> = [
  { value: 'agent', label: 'Agent chat', icon: 'mdi-robot-outline' },
  { value: 'compare', label: 'Model compare', icon: 'mdi-compare-horizontal' },
  { value: 'history', label: 'Run history', icon: 'mdi-history' },
  { value: 'about', label: 'About', icon: 'mdi-information-outline' },
]

onMounted(loadInfo)
onBeforeUnmount(() => window.clearTimeout(infoTimer))
</script>

<template>
  <v-app>
    <v-app-bar class="fg-appbar" flat height="68">
      <template #prepend>
        <div class="ml-3 d-flex align-center">
          <FoundryLogo :size="38" inverted />
        </div>
      </template>
      <v-app-bar-title>
        <div class="d-flex flex-column">
          <span class="text-h6 font-weight-bold" style="line-height: 1.2">Foundry Guide</span>
          <span class="text-caption" style="opacity: 0.9">Microsoft Foundry Agent Service demo</span>
        </div>
      </v-app-bar-title>
      <template #append>
        <v-chip
          class="mr-2 d-none d-sm-flex"
          :prepend-icon="agentStatus.icon"
          variant="flat"
          color="white"
          size="small"
          data-testid="agent-status"
        >
          <span :class="`text-${agentStatus.color}`">{{ agentStatus.label }}</span>
          <span v-if="info?.agent.version" class="ml-1 text-medium-emphasis">v{{ info.agent.version }}</span>
        </v-chip>
        <v-btn
          icon
          variant="text"
          color="white"
          data-testid="theme-toggle"
          :aria-label="isDark ? 'Switch to light theme' : 'Switch to dark theme'"
          @click="toggleTheme"
        >
          <v-icon>{{ isDark ? 'mdi-white-balance-sunny' : 'mdi-weather-night' }}</v-icon>
          <v-tooltip activator="parent" location="bottom">{{ isDark ? 'Light theme' : 'Dark theme' }}</v-tooltip>
        </v-btn>
      </template>
    </v-app-bar>

    <v-main>
      <v-container class="py-4" style="max-width: 1320px">
        <v-tabs v-model="tab" color="primary" class="mb-4" show-arrows>
          <v-tab
            v-for="item in tabs"
            :key="item.value"
            :value="item.value"
            :prepend-icon="item.icon"
            :data-testid="`tab-${item.value}`"
          >
            {{ item.label }}
          </v-tab>
        </v-tabs>

        <v-alert v-if="infoError" type="warning" variant="tonal" density="compact" class="mb-4" closable>
          Could not load deployment info: {{ infoError }}
        </v-alert>
        <v-alert
          v-else-if="info && !info.configured"
          type="info"
          variant="tonal"
          density="compact"
          class="mb-4"
          title="Microsoft Foundry is not configured"
        >
          Set <code>FOUNDRY_PROJECT_ENDPOINT</code> (and the model deployment variables) to enable the agent.
        </v-alert>

        <v-window v-model="tab" class="mx-n3 px-3 my-n2 py-2">
          <v-window-item value="agent">
            <AgentChat :info="info" />
          </v-window-item>
          <v-window-item value="compare">
            <ModelCompare :info="info" />
          </v-window-item>
          <v-window-item value="history">
            <RunHistory :active="tab === 'history'" />
          </v-window-item>
          <v-window-item value="about">
            <AboutPanel :info="info" />
          </v-window-item>
        </v-window>
      </v-container>
    </v-main>

    <v-footer class="text-caption text-medium-emphasis justify-center flex-wrap ga-3 py-2" color="transparent">
      <span><v-icon size="14" icon="mdi-cloud-outline" /> {{ info?.endpoint_host ?? 'endpoint not configured' }}</span>
      <span v-if="info"><v-icon size="14" icon="mdi-brain" /> {{ info.models.primary }} / {{ info.models.fast }}</span>
      <span v-if="info">
        <v-icon size="14" icon="mdi-robot-outline" /> {{ info.agent.name }}{{
          info.agent.version ? ` v${info.agent.version}` : ''
        }}
      </span>
      <span v-if="info"><v-icon size="14" icon="mdi-map-marker-outline" /> {{ info.region }}</span>
      <span v-if="info"><v-icon size="14" icon="mdi-source-commit" /> {{ info.app_version }}</span>
    </v-footer>
  </v-app>
</template>
