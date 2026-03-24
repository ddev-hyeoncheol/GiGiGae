import { ref, watch } from 'vue'

const STORAGE_KEY = 'gigigae-dark-mode'

const isDark = ref<boolean>(localStorage.getItem(STORAGE_KEY) === 'true')

function applyTheme(dark: boolean) {
  document.documentElement.classList.toggle('dark', dark)
}

// 초기 적용
applyTheme(isDark.value)

watch(isDark, (val) => {
  applyTheme(val)
  localStorage.setItem(STORAGE_KEY, String(val))
})

export function useDarkMode() {
  const toggle = () => {
    isDark.value = !isDark.value
  }
  return { isDark, toggle }
}
