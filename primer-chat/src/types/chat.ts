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
	index: string
	data: ChatMessage
	timestamp: string
}

export interface ClientChatMessage {
	index: string
	data: ChatMessage
}

export interface ApiChatMetaResponse {
	history_id: string
	files: ApiFileResponse[]
	messages: ApiChatMessageResponse[]
}
