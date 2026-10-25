import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/api': {
        target: 'https://expense-tracker-api-n5s7.onrender.com',
        changeOrigin: true,
        secure: true,
      },
    },
  },
})
