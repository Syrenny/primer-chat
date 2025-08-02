import {
	type ApiCompletionsChunkResponse,
	ChunkType,
} from '../types/completions'
import apiClient from './base'

// Получение буфера результатов
export const apiCompletionsBuffer = async (): Promise<void> => {
	await apiClient.get('/api/completions/buffer')
}

// Отправка запроса на генерацию и стриминг
export const apiCompletionsCreate = async (
	historyId: string,
	query: string,
	onData: (chunk: ApiCompletionsChunkResponse) => void,
	onDone?: () => void,
	onError?: (error: unknown) => void
): Promise<void> => {
	const request = {
		historyId: historyId,
		query: query,
	}
	try {
		const response = await fetch('/api/completions', {
			method: 'POST',
			credentials: 'include',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify(request),
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
