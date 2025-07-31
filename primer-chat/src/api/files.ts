import type {
	ApiFileResponse,
	ApiFileLinkResponse,
	ApiFileStatusResponse,
} from '@/types/files'
import apiClient from './base'

// Получить список файлов
export const apiFileList = async (): Promise<ApiFileResponse[]> => {
	const { data } = await apiClient.get('/api/files')
	return data
}

// Загрузить файл (multipart/form-data)
export const apiFileUpload = async (file: File): Promise<void> => {
	const formData = new FormData()
	formData.append('file', file)
	await apiClient.post('/api/files', formData)
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
