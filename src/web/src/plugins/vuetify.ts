import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'
import { createVuetify, type ThemeDefinition } from 'vuetify'
import { aliases, mdi } from 'vuetify/iconsets/mdi'

export const THEME_STORAGE_KEY = 'foundry-guide-theme'

const foundryLight: ThemeDefinition = {
  dark: false,
  colors: {
    background: '#F6F7FB',
    surface: '#FFFFFF',
    'surface-variant': '#EEF0F8',
    'on-surface-variant': '#1B1B2F',
    primary: '#6B46FF',
    secondary: '#0F6CBD',
    accent: '#00A3C4',
    info: '#0F6CBD',
    success: '#107C10',
    warning: '#C27C0E',
    error: '#C50F1F',
  },
}

const foundryDark: ThemeDefinition = {
  dark: true,
  colors: {
    background: '#0F1020',
    surface: '#1A1B2E',
    'surface-variant': '#26283F',
    'on-surface-variant': '#E6E6F5',
    primary: '#9D8BFF',
    secondary: '#5CB3FF',
    accent: '#3DD6F5',
    info: '#5CB3FF',
    success: '#6CCB5F',
    warning: '#FCE100',
    error: '#FF99A4',
  },
}

function initialTheme(): 'foundryLight' | 'foundryDark' {
  const stored = window.localStorage.getItem(THEME_STORAGE_KEY)
  if (stored === 'foundryLight' || stored === 'foundryDark') return stored
  return window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'foundryDark' : 'foundryLight'
}

export default createVuetify({
  icons: { defaultSet: 'mdi', aliases, sets: { mdi } },
  theme: {
    defaultTheme: initialTheme(),
    themes: { foundryLight, foundryDark },
  },
  defaults: {
    VCard: { rounded: 'lg' },
    VBtn: { rounded: 'lg', class: 'text-none' },
    VTab: { class: 'text-none' },
    VChip: { rounded: 'lg' },
    VTextField: { variant: 'outlined', density: 'comfortable' },
    VTextarea: { variant: 'outlined', density: 'comfortable' },
    VSelect: { variant: 'outlined', density: 'comfortable' },
  },
})
