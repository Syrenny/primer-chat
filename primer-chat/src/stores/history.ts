import { v4 as uuidv4 } from 'uuid'
import { createStore } from 'zustand'
import { apiChatMessages } from '../api/history'
import type { ApiChatMessageResponse, ClientChatMessage } from '../types/chat'
import { RoleType } from '../types/chat'
export interface HistoryState {
	messages: ClientChatMessage[]
	isHistoryLoading: boolean

	loadHistory: (historyId: string) => Promise<void>
	addUserMessage: (content: string) => void
	updateAssistantMessage: (content: string) => void
	clearHistory: () => void
}

export const historyStore = createStore<HistoryState>((set, get) => ({
	messages: [],
	isHistoryLoading: true,

	loadHistory: async historyId => {
		set({ isHistoryLoading: true })
		try {
			const history = await apiChatMessages(historyId)
			const clientMessages: ClientChatMessage[] = history.map(
				(msg: ApiChatMessageResponse) => ({
					index: msg.index ?? uuidv4(),
					data: msg.data,
				})
			)
			set({ messages: clientMessages })
		} catch (error) {
			console.error('❌ Error loading chat history:', error)
		} finally {
			set({ isHistoryLoading: false })
		}
	},

	addUserMessage: (content: string) => {
		const newMessage: ClientChatMessage = {
			index: uuidv4(),
			data: { role: RoleType.User, content },
		}
		set(state => ({
			messages: [...state.messages, newMessage],
		}))
	},

	updateAssistantMessage: (content: string) => {
		set(state => {
			console.log('Updating assistant message: ', content)
			const prev = state.messages
			const last = prev[prev.length - 1]

			// Если нет сообщения ассистента — создаём новое
			if (!last || last.data.role !== 'assistant') {
				return {
					messages: [
						...prev,
						{
							index: uuidv4(),
							data: { role: RoleType.Assistant, content },
						},
					],
				}
			}

			// Обновляем последнее
			const updated = {
				...last,
				data: {
					...last.data,
					content: last.data.content + content,
				},
			}

			return {
				messages: [...prev.slice(0, -1), updated],
			}
		})
	},

	clearHistory: () => set({ messages: [] }),
}))
