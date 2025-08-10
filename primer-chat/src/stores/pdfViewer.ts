import type { IndexedChunk } from '@/types/chunks'
import { createStore } from 'zustand'

interface PDFViewerStore {
	iframeRef: HTMLIFrameElement | null
	setIframeRef: (ref: HTMLIFrameElement | null) => void
	highlightPositions: (positions: IndexedChunk['positions']) => void
}

export const pdfViewerStore = createStore<PDFViewerStore>((set, get) => ({
	iframeRef: null,
	setIframeRef: ref => set({ iframeRef: ref }),

	highlightPositions: positions => {
		const iframe = get().iframeRef
		if (!iframe) return
		iframe.contentWindow?.postMessage(
			{
				type: 'highlight-chunk',
				payload: { positions },
			},
			'*'
		)
	},
}))
