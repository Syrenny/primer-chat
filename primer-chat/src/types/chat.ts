import type { IndexedChunk } from './chunks'
import type { ApiFileResponse } from './files'

export const RoleType = {
	System: 'system',
	User: 'user',
	Assistant: 'assistant',
	Function: 'function',
} as const

export type RoleType = (typeof RoleType)[keyof typeof RoleType]

export interface ChatMessage {
	role: RoleType
	content: string
	name?: string | null
}

export interface ApiChatMessageResponse {
	request_id: string
	history_id: string
	timestamp: string
	chunks: IndexedChunk[]
	user_message: ChatMessage
	assistant_message?: ChatMessage
}

export interface ClientChatRequest {
	requestId: string
	historyId: string
	timestamp: string
	chunks: IndexedChunk[]
	userMessage: ChatMessage
	assistantMessage?: ChatMessage
}

export interface ApiChatMetaResponse {
	history_id: string
	files: ApiFileResponse[]
	requests: ApiChatMessageResponse[]
}
