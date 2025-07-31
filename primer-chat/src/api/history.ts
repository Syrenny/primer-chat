import type { ApiChatMessageResponse, ApiChatMetaResponse } from '../types/chat'
import apiClient from './base'

// Получить все сообщения по истории
export const apiChatMessages = async (
	historyId: string
): Promise<ApiChatMessageResponse[]> => {
	const { data } = await apiClient.get(`/api/history_messages/${historyId}`)
	return data
}

// Получить список чатов
export const apiChatList = async (): Promise<ApiChatMetaResponse[]> => {
	const { data } = await apiClient.get('/api/history_meta')
	return data
}

// Создать новый чат с файлами
export const apiChatCreate = async (
	fileIds: string[]
): Promise<ApiChatMetaResponse> => {
	const { data } = await apiClient.post('/api/history_meta', {
		file_ids: fileIds,
	})
	return data
}

// Получить мета-данные конкретного чата
export const apiChatGet = async (
	historyId: string
): Promise<ApiChatMetaResponse> => {
	const { data } = await apiClient.get(`/api/history_meta/${historyId}`)
	return data
}

// Удалить чат
export const apiChatDelete = async (historyId: string): Promise<void> => {
	await apiClient.delete(`/api/history_meta/${historyId}`)
}

// Обновить чат (например, привязать новые файлы)
export const apiChatUpdate = async (
	historyId: string,
	fileIds: string[]
): Promise<ApiChatMetaResponse> => {
	const { data } = await apiClient.patch(`/api/history_meta/${historyId}`, {
		file_ids: fileIds,
	})
	return data
}
