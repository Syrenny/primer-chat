import {
	apiChatCreate,
	apiChatDelete,
	apiChatGet,
	apiChatList,
	apiChatUpdate,
} from '@/api/history'
import type { ApiChatMetaResponse } from '@/types/chat'
import { createStore } from 'zustand'

interface ChatMetaStoreState {
	chats: ApiChatMetaResponse[]
	loading: boolean
	error: string | null

	fetchChats: () => Promise<void>
	createChat: (fileIds: string[]) => Promise<ApiChatMetaResponse | null>
	deleteChat: (historyId: string) => Promise<void>
	updateChat: (
		historyId: string,
		fileIds: string[]
	) => Promise<ApiChatMetaResponse | null>
	getChatById: (historyId: string) => Promise<ApiChatMetaResponse | null>
}

export const chatMetaStore = createStore<ChatMetaStoreState>((set, get) => ({
	chats: [],
	loading: false,
	error: null,

	fetchChats: async () => {
		set({ loading: true, error: null })
		try {
			const chats = await apiChatList()
			set({ chats })
		} catch (error) {
			console.error(error)
			set({ error: 'Не удалось загрузить список чатов' })
		} finally {
			set({ loading: false })
		}
	},

	createChat: async fileIds => {
		set({ loading: true, error: null })
		try {
			const chat = await apiChatCreate(fileIds)
			set({ chats: [...get().chats, chat] })
			return chat
		} catch (error) {
			console.error(error)
			set({ error: 'Ошибка при создании чата' })
			return null
		} finally {
			set({ loading: false })
		}
	},

	deleteChat: async historyId => {
		set({ loading: true, error: null })
		try {
			await apiChatDelete(historyId)
			const filtered = get().chats.filter(
				chat => chat.history_id !== historyId
			)
			set({ chats: filtered })
		} catch (error) {
			console.error(error)
			set({ error: 'Ошибка при удалении чата' })
		} finally {
			set({ loading: false })
		}
	},

	updateChat: async (historyId, fileIds) => {
		set({ loading: true, error: null })
		try {
            console.log("Request:", fileIds)
			const updated = await apiChatUpdate(historyId, fileIds)
            console.log("Updated:", updated)
			const updatedChats = get().chats.map(chat =>
				chat.history_id === historyId ? updated : chat
			)
			set({ chats: updatedChats })
			return updated
		} catch (error) {
			console.error(error)
			set({ error: 'Ошибка при обновлении чата' })
			return null
		} finally {
			set({ loading: false })
		}
	},

	getChatById: async historyId => {
		set({ loading: true, error: null })
		try {
			const chat = await apiChatGet(historyId)
			return chat
		} catch (error) {
			console.error(error)
			set({ error: 'Ошибка при получении чата' })
			return null
		} finally {
			set({ loading: false })
		}
	},
}))
