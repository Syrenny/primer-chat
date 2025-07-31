export const ChunkType = {
	Default: 'default',
	Error: 'error',
} as const

export type ChunkType = (typeof ChunkType)[keyof typeof ChunkType]

export interface ApiCompletionsChunkResponse {
	type: ChunkType
	text: string
}
