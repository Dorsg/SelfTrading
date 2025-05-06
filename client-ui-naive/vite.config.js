import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
      'ag-grid-community': path.resolve(__dirname, 'node_modules/ag-grid-community'),
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/auth': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/account': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/orders': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/executed-trades': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/runners': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/ib/status': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
