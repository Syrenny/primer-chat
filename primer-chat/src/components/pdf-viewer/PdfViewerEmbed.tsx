import { pdfViewerStore } from '@/stores/pdfViewer'
import { useTheme } from 'next-themes'
import { useEffect, useRef } from 'react'
import { useStore } from 'zustand'

export function PDFViewerEmbed({ fileUrl }: { fileUrl: string }) {
	const { resolvedTheme } = useTheme() // resolvedTheme = 'light' | 'dark'
	const iframeRef = useRef<HTMLIFrameElement>(null)
	const setIframeRef = useStore(pdfViewerStore, s => s.setIframeRef)

	useEffect(() => {
		if (iframeRef.current) {
			setIframeRef(iframeRef.current)
		}
	}, [iframeRef.current])

	const viewerSrc = `/pdfjs/web/viewer.html?file=${encodeURIComponent(
		fileUrl
	)}&theme=${resolvedTheme}`

	return (
		<iframe
			ref={iframeRef}
			src={viewerSrc}
			className='w-full h-full border-none'
			title='PDF Viewer'
		/>
	)
}
