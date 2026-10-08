import { onMounted, type Ref } from 'vue'

/**
 * Vuetify places data-* attributes on the field wrapper. Put the test id on the native
 * input/textarea instead so Playwright's `fill()` works on `getByTestId(...)`.
 */
export function useNativeTestId(fieldRef: Ref<{ $el?: Element } | null>, testId: string, selector = 'input, textarea') {
  onMounted(() => {
    const element = fieldRef.value?.$el?.querySelector(selector)
    element?.setAttribute('data-testid', testId)
  })
}
