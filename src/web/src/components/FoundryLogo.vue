<script setup lang="ts">
import { useId } from 'vue'

withDefaults(defineProps<{ size?: number; inverted?: boolean }>(), { size: 36, inverted: false })
const gradientId = `fg-logo-${useId()}`
</script>

<template>
  <svg
    :width="size"
    :height="size"
    viewBox="0 0 64 64"
    role="img"
    aria-label="Foundry Guide logo"
    xmlns="http://www.w3.org/2000/svg"
  >
    <defs>
      <linearGradient :id="gradientId" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stop-color="#7B4DFF" />
        <stop offset="0.55" stop-color="#3B6CF6" />
        <stop offset="1" stop-color="#00B4D8" />
      </linearGradient>
    </defs>
    <rect width="64" height="64" rx="14" :fill="inverted ? '#FFFFFF' : `url(#${gradientId})`" />
    <path d="M20 46V18h24v6H27v6h14v6H27v10z" :fill="inverted ? `url(#${gradientId})` : '#FFFFFF'" />
    <circle cx="46" cy="42" r="5" :fill="inverted ? `url(#${gradientId})` : '#FFFFFF'" opacity="0.9" />
  </svg>
</template>
