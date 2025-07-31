import {
	type ApiCompletionsChunkResponse,
	ChunkType,
} from '../types/completions'
import apiClient from './base'

// Отправка запроса на генерацию
export const apiCompletionsCreate = async (
	historyId: string,
	query: string
): Promise<void> => {
	await apiClient.post('/api/completions', {
		history_id: historyId,
		query: query,
	})
}

// Получение буфера результатов
export const apiCompletionsBuffer = async (): Promise<void> => {
	await apiClient.get('/api/completions/buffer')
}

// Стриминг генерации
export const apiCompletionsStream = async (
	onData: (chunk: ApiCompletionsChunkResponse) => void,
	onDone?: () => void,
	onError?: (error: unknown) => void
): Promise<void> => {
	try {
		const response = await fetch('/api/completions/stream', {
			method: 'GET',
			credentials: 'include',
			headers: {
				'Content-Type': 'application/json',
			},
		})

		if (!response.ok || !response.body) {
			throw new Error(`Stream error: ${response.status}`)
		}

		const reader = response.body.getReader()
		const decoder = new TextDecoder('utf-8')
		let partial = ''

		while (true) {
			const { value, done } = await reader.read()
			if (done) break

			partial += decoder.decode(value, { stream: true })
			const lines = partial.split('\n\n')

			// Оставляем последний кусок на следующий цикл (вдруг неполный JSON)
			partial = lines.pop() || ''

			for (const line of lines) {
				const trimmed = line.trim()
				if (!trimmed) continue

				try {
					const parsed: ApiCompletionsChunkResponse =
						JSON.parse(trimmed)
					onData(parsed)
				} catch {
					// fallback: просто передаём как текст, если это невалидный JSON
					onData({ type: ChunkType.Default, text: trimmed })
				}
			}
		}

		// Остаток после выхода из цикла
		if (partial.trim()) {
			try {
				const parsed: ApiCompletionsChunkResponse = JSON.parse(
					partial.trim()
				)
				onData(parsed)
			} catch {
				onData({ type: ChunkType.Default, text: partial.trim() })
			}
		}

		onDone?.()
	} catch (error) {
		console.error('[apiCompletionsStream] ❌', error)
		onError?.(error)
	}
}
