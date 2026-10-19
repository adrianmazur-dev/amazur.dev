import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  vite: {
    plugins: [tailwindcss()],
    server: {
      proxy: {
        '/health': {
          target: 'http://127.0.0.1:8000',
        },
        '/linkedin/profile': {
          target: 'http://127.0.0.1:8000',
        },
      },
    },
  },
});
