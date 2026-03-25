import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    watch: {
      usePolling: true,
      interval: 500,
    },
    proxy: {
      '/api': {
        target: process.env.API_URL || 'http://localhost:9000',
        changeOrigin: true,
      },
      '/image': {
        target: process.env.API_URL || 'http://localhost:9000',
        changeOrigin: true,
      },
    },
  },
})
