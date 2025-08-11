import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
	plugins: [react(), tailwindcss()],
	resolve: {
		alias: {
			'@': path.resolve(__dirname, './src'),
		},
	},
	build: {
		outDir: 'build',
	},
	server: {
		host: true,
		proxy: {
			'/api': 'http://localhost:8000',
			'/primer-chat-pdf': 'http://0.0.0.0:9000',
		},
	},
})
