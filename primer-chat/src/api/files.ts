import {
	type ApiFileLinkResponse,
	type ApiFileResponse,
	type ApiFileStatusResponse,
	type ApiFileUploadProgress,
} from '@/types/files'
import apiClient from './base'

// Получить список файлов
export const apiFileList = async (): Promise<ApiFileResponse[]> => {
	const { data } = await apiClient.get('/api/files')
	return data
}

export const apiFileUpload = async (
	file: File,
	onData: (progress: ApiFileUploadProgress) => void,
	onDone?: () => void,
	onError?: (error: unknown) => void
): Promise<void> => {
	const formData = new FormData()
	formData.append('file', file)

	try {
		const response = await fetch('/api/files', {
			method: 'POST',
			credentials: 'include',
			body: formData,
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

				const parsed: ApiFileUploadProgress = JSON.parse(trimmed)
                console.log(parsed)
                onData(parsed)
			}
		}

		// Остаток после выхода из цикла
		if (partial.trim()) {
			const parsed: ApiFileUploadProgress = JSON.parse(partial.trim())
			onData(parsed)
		}

		onDone?.()
	} catch (error) {
		console.error('[apiCompletionsStream] ❌', error)
		onError?.(error)
	}
}

// Получить статус обработки файла
export const apiFileStatus = async (
	fileId: string
): Promise<ApiFileStatusResponse> => {
	const { data } = await apiClient.get(`/api/files/${fileId}/status`)
	return data
}

// Удалить файл
export const apiFileDelete = async (fileId: string): Promise<void> => {
	await apiClient.delete(`/api/files/${fileId}`)
}

// Получить подписанную ссылку на файл
export const apiFileLink = async (
	fileId: string
): Promise<ApiFileLinkResponse> => {
	const { data } = await apiClient.get(`/api/files/${fileId}/signed_url`)
	return data
}
