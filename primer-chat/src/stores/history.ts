import { v4 as uuidv4 } from 'uuid'
import { createStore } from 'zustand'
import { apiChatMessages } from '../api/history'
import type { ApiChatMessageResponse, ClientChatRequest } from '../types/chat'
import { RoleType } from '../types/chat'
import type { IndexedChunk } from '../types/chunks'

export interface HistoryState {
	requests: ClientChatRequest[]
	isHistoryLoading: boolean

	loadHistory: (historyId: string) => Promise<void>
	startUserRequest: (historyId: string, content: string) => string
	attachRetrievedChunks: (chunks: IndexedChunk) => void
	updateAssistantMessage: (content: string) => void
    failLastRequest: (errorText: string) => void

	clearHistory: () => void
}

export const historyStore = createStore<HistoryState>((set, _) => ({
	requests: [],
	isHistoryLoading: true,

	loadHistory: async historyId => {
		set({ isHistoryLoading: true })
		try {
			const history = await apiChatMessages(historyId)
			const messages: ClientChatRequest[] = history.map(
				(msg: ApiChatMessageResponse) => ({
					requestId: msg.request_id,
					historyId: msg.history_id,
					timestamp: msg.timestamp,
					chunks: msg.chunks,
					userMessage: msg.user_message,
					assistantMessage: msg.assistant_message,
				})
			)
			set({ requests: messages })
		} catch (error) {
			console.error('❌ Error loading chat history:', error)
		} finally {
			set({ isHistoryLoading: false })
		}
	},

	startUserRequest: (historyId, content) => {
		const requestId = uuidv4()
		const newRequest: ClientChatRequest = {
			requestId,
			historyId,
			timestamp: new Date().toISOString(),
			chunks: [],
			userMessage: {
				role: RoleType.User,
				content,
			},
		}
		set(state => ({ requests: [...state.requests, newRequest] }))
		return requestId
	},

	attachRetrievedChunks: chunk => {
		set(state => {
			if (state.requests.length === 0) return state
			const prev = state.requests
			const last = prev[prev.length - 1]
			const updated: ClientChatRequest = {
				...last,
				chunks: [...last.chunks, chunk], // важный момент: заменяем на актуальные из сервера
			}
			return { requests: [...prev.slice(0, -1), updated] }
		})
	},

	updateAssistantMessage: content => {
		if (!content) return
		set(state => {
			const prev = state.requests
			if (prev.length === 0) return state
			const last = prev[prev.length - 1]

			const updated: ClientChatRequest = !last.assistantMessage
				? {
						...last,
						assistantMessage: { role: RoleType.Assistant, content },
				  }
				: {
						...last,
						assistantMessage: {
							...last.assistantMessage,
							content: last.assistantMessage.content + content,
						},
				  }

			return { requests: [...prev.slice(0, -1), updated] }
		})
	},

	failLastRequest: errorText => {
		set(state => {
			const prev = state.requests
			if (prev.length === 0) return state
			const last = prev[prev.length - 1]
			const updated: ClientChatRequest = {
				...last,
				assistantMessage: {
					role: RoleType.Assistant,
					content:
						(last.assistantMessage?.content || '') +
						`\n\n⚠️ ${errorText}`,
				},
			}
			return { requests: [...prev.slice(0, -1), updated] }
		})
	},
	clearHistory: () => set({ requests: [] }),
}))
