import { createStore } from 'zustand'
import { apiCompletionsCreate } from '../api/completions'
import type { ApiCompletionsChunkResponse } from '../types/completions'
import { ChunkType } from '../types/completions'
import { historyStore } from './history'

interface GenerationState {
	isGenerating: boolean
	isWaitingForGeneration: boolean
	startGeneration: (
		query: string,
		historyId: string,
		opts: {
			onData?: (data: string) => void
			onDone?: () => void
			onError?: (error: string) => void
		}
	) => Promise<void>
}

export const generationStore = createStore<GenerationState>((set, get) => ({
	isGenerating: false,
	isWaitingForGeneration: false,

	startGeneration: async (query, historyId, { onData, onDone, onError }) => {
		const { isGenerating, isWaitingForGeneration } = get()
		if (isGenerating || isWaitingForGeneration) return

		historyStore.getState().startUserRequest(historyId, query)

		set({ isWaitingForGeneration: true })

		await apiCompletionsCreate(
			historyId,
			query,
			(chunk: ApiCompletionsChunkResponse) => {
				const state = get()
				if (state.isWaitingForGeneration)
					set({ isWaitingForGeneration: false })
				if (!state.isGenerating) set({ isGenerating: true })

				if (chunk.type === ChunkType.Retrieved) {
					historyStore
						.getState()
						.attachRetrievedChunks({
							positions: chunk.positions,
							file_id: chunk.file_id,
							filename: chunk.filename,
						})
					return
				}

				if (chunk.type === ChunkType.Error) {
					console.error('Error chunk received:', chunk)
					set({ isGenerating: false, isWaitingForGeneration: false })
					onError?.(chunk.text)
					return
				}
				if (chunk.text) {
					historyStore.getState().updateAssistantMessage(chunk.text)
					onData?.(chunk.text)
				}
			},
			() => {
				set({ isGenerating: false, isWaitingForGeneration: false })
				onDone?.()
			},
			err => {
				set({ isGenerating: false, isWaitingForGeneration: false })
				const msg = (err as any)?.message || 'Stream aborted'
				historyStore.getState().failLastRequest(msg)
				onError?.(msg)
			}
		)
	},
}))
