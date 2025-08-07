import { createStore } from 'zustand'

interface PDFViewerStore {
	iframeRef: HTMLIFrameElement | null
	setIframeRef: (ref: HTMLIFrameElement | null) => void
	scrollToChunk: (chunk: Chunk) => void
}

export const pdfViewerStore = createStore<PDFViewerStore>((set, get) => ({
	iframeRef: null,
	setIframeRef: ref => set({ iframeRef: ref }),

	scrollToChunk: chunk => {
		const iframe = get().iframeRef
		if (!iframe) return

		iframe.contentWindow?.postMessage(
			{
				type: 'scroll-to-chunk',
				payload: chunk,
			},
			'*'
		)
	},
}))
