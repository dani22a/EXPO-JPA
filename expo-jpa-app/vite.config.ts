import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// El proxy reenvía /api -> Spring Boot en :8080.
// Así evitamos CORS sin tocar el backend.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
      },
    },
  },
});
