import react from '@vitejs/plugin-react'
import { defineConfig, loadEnv, type UserConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'

export function createViteConfig(
  mode: string,
  env = loadEnv(mode, process.cwd(), 'API_PROXY_TARGET'),
): UserConfig {
  const target = env.API_PROXY_TARGET?.trim() || 'http://127.0.0.1:8000'

  return {
    plugins: [react(), tailwindcss()],
    server: {
      proxy: {
        '/api': {
          target,
          changeOrigin: true,
        },
      },
    },
  }
}

export default defineConfig(({ mode }) => createViteConfig(mode))
