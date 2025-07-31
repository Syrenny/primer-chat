import { create } from 'zustand'
import { apiCompletionsCreate, apiCompletionsStream } from '../api/completions'
import type { ApiCompletionsChunkResponse } from '../types/completions'

interface GenerationState {
	isGenerating: boolean
	isWaitingForGeneration: boolean
	startGeneration: (
		query: string,
		historyId: string,
		opts: {
			onData: (data: string) => void
			onDone?: () => void
			onError?: (error: string) => void
		}
	) => Promise<void>
}

export const useGenerationStore = create<GenerationState>((set, get) => ({
	isGenerating: false,
	isWaitingForGeneration: false,

	startGeneration: async (query, historyId, { onData, onDone, onError }) => {
		const { isGenerating, isWaitingForGeneration } = get()
		if (isGenerating || isWaitingForGeneration) return

		set({ isWaitingForGeneration: true })

		await apiCompletionsCreate(historyId, query)

        // TODO: get rid of timeout
        await new Promise(resolve => setTimeout(resolve, 5000))

		await apiCompletionsStream(
			(chunk: ApiCompletionsChunkResponse) => {
				const state = get()
				if (state.isWaitingForGeneration)
					set({ isWaitingForGeneration: false })
				if (!state.isGenerating) set({ isGenerating: true })

				if (chunk.type === 'error') {
					console.error('Error chunk received:', chunk)
					set({ isGenerating: false, isWaitingForGeneration: false })
					onError?.(chunk.text)
					return
				}

				onData(chunk.text)
			},
			() => {
				set({ isGenerating: false, isWaitingForGeneration: false })
				onDone?.()
			},
			() => {
				set({ isGenerating: false, isWaitingForGeneration: false })
			}
		)
	},
}))
