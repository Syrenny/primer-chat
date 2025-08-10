import type { PdfLinePosition } from './chunks'

export const ChunkType = {
	Response: 'response',
	Retrieved: 'retrieved',
	Error: 'error',
} as const

export type ApiCompletionsChunkResponse =
	| {
			type: typeof ChunkType.Retrieved
			positions: PdfLinePosition[]
			file_id: string
			filename: string
	  }
	| { type: typeof ChunkType.Response; text: string }
	| { type: typeof ChunkType.Error; text: string }
