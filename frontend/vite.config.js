import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
    plugins: [react()],
    server: {
        port: 5173,
        proxy: {
            '/upload-resume': 'http://localhost:8000',
            '/run-search': 'http://localhost:8000',
            '/jobs': 'http://localhost:8000',
            '/job-stats': 'http://localhost:8000',
            '/profile': 'http://localhost:8000',
            '/update-status': 'http://localhost:8000',
        },
    },
})
