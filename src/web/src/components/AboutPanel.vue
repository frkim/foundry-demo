<script setup lang="ts">
import { computed } from 'vue'
import type { InfoResponse } from '../types'

const props = defineProps<{ info: InfoResponse | null }>()

const flow = [
  {
    icon: 'mdi-monitor',
    title: 'Vue 3 + Vuetify SPA',
    text: 'Served by the API container. Agent chat, model compare and run history.',
  },
  {
    icon: 'mdi-language-python',
    title: 'FastAPI on Azure Container Apps',
    text: 'Keyless: user-assigned managed identity + DefaultAzureCredential. azure-ai-projects 2.x + openai.',
  },
  {
    icon: 'mdi-robot-outline',
    title: 'Foundry Agent Service',
    text: 'Prompt agent (agents.create_version + PromptAgentDefinition) invoked through the Responses API with conversations.',
  },
  {
    icon: 'mdi-tools',
    title: 'Tools',
    text: 'Microsoft Learn MCP server (learn.microsoft.com/api/mcp) and the Code Interpreter sandbox.',
  },
  {
    icon: 'mdi-chart-timeline-variant',
    title: 'Observability',
    text: 'OpenTelemetry GenAI traces and structured logs exported to Application Insights.',
  },
]

const details = computed(() => {
  const info = props.info
  return [
    { label: 'Project endpoint host', value: info?.endpoint_host ?? 'not configured', icon: 'mdi-cloud-outline' },
    { label: 'Foundry project', value: info?.project_name ?? '—', icon: 'mdi-folder-outline' },
    { label: 'Region', value: info?.region ?? '—', icon: 'mdi-map-marker-outline' },
    { label: 'Primary (agent) model', value: info?.models.primary ?? '—', icon: 'mdi-brain' },
    { label: 'Fast model', value: info?.models.fast ?? '—', icon: 'mdi-lightning-bolt' },
    {
      label: 'Agent',
      value: info ? `${info.agent.name}${info.agent.version ? ` v${info.agent.version}` : ''} (${info.agent.status})` : '—',
      icon: 'mdi-robot-outline',
    },
    { label: 'Agent tools', value: info?.agent.tools.join(' · ') ?? '—', icon: 'mdi-tools' },
    { label: 'Telemetry', value: info?.telemetry_enabled ? 'Application Insights' : 'disabled', icon: 'mdi-chart-line' },
    { label: 'App version', value: info?.app_version ?? '—', icon: 'mdi-source-commit' },
  ]
})

const links = [
  { title: 'What is Microsoft Foundry?', href: 'https://learn.microsoft.com/azure/foundry/what-is-foundry' },
  { title: 'Foundry Agent Service overview', href: 'https://learn.microsoft.com/azure/foundry/agents/overview' },
  { title: 'Agent tool catalog', href: 'https://learn.microsoft.com/azure/foundry/agents/concepts/tool-catalog' },
  {
    title: 'Responses API in Foundry',
    href: 'https://learn.microsoft.com/azure/foundry/openai/how-to/responses',
  },
  {
    title: 'Microsoft Learn MCP server',
    href: 'https://learn.microsoft.com/training/support/mcp',
  },
  { title: 'azure-ai-projects (Python)', href: 'https://learn.microsoft.com/python/api/overview/azure/ai-projects-readme' },
  { title: 'Source code: frkim/foundry-demo', href: 'https://github.com/frkim/foundry-demo' },
]
</script>

<template>
  <v-row>
    <v-col cols="12" lg="7">
      <v-card elevation="1" height="100%">
        <v-card-item>
          <template #prepend>
            <v-avatar color="primary" variant="tonal" rounded="lg"><v-icon icon="mdi-sitemap-outline" /></v-avatar>
          </template>
          <v-card-title>Architecture</v-card-title>
          <v-card-subtitle>Microsoft Foundry (new) · Foundry resource + project · keyless</v-card-subtitle>
        </v-card-item>
        <v-card-text>
          <v-timeline side="end" density="compact" align="start" truncate-line="both">
            <v-timeline-item v-for="step in flow" :key="step.title" dot-color="primary" :icon="step.icon" size="small">
              <div class="font-weight-bold">{{ step.title }}</div>
              <div class="text-body-2 text-medium-emphasis">{{ step.text }}</div>
            </v-timeline-item>
          </v-timeline>
        </v-card-text>
      </v-card>
    </v-col>
    <v-col cols="12" lg="5">
      <v-card elevation="1" class="mb-4" data-testid="deployment-info">
        <v-card-item>
          <v-card-title>Deployment</v-card-title>
          <v-card-subtitle>From <code>/api/info</code></v-card-subtitle>
        </v-card-item>
        <v-list density="compact" lines="two">
          <v-list-item v-for="item in details" :key="item.label" :prepend-icon="item.icon" :title="item.value" :subtitle="item.label" />
        </v-list>
      </v-card>
      <v-card elevation="1">
        <v-card-item><v-card-title>Learn more</v-card-title></v-card-item>
        <v-list density="compact">
          <v-list-item
            v-for="link in links"
            :key="link.href"
            :href="link.href"
            target="_blank"
            rel="noopener"
            prepend-icon="mdi-open-in-new"
            :title="link.title"
          />
        </v-list>
      </v-card>
    </v-col>
  </v-row>
</template>
