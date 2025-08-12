import { pdfViewerStore } from '@/stores/pdfViewer'
import { useTheme } from 'next-themes'
import { useEffect, useMemo, useRef } from 'react'
import { useStore } from 'zustand'

import pdfBridgeCssUrl from './pdfjs-plugins/pdf-theme-bridge.css?url'
import scrollHandlerJsUrl from './pdfjs-plugins/scrollHandler.js?url'

export function PDFViewerEmbed({ fileUrl }: { fileUrl: string }) {
	const { resolvedTheme = 'light' } = useTheme()
	const iframeRef = useRef<HTMLIFrameElement>(null)
	const setIframeRef = useStore(pdfViewerStore, s => s.setIframeRef)

	const viewerSrc = useMemo(
		() =>
			`/pdfjs/web/viewer.html?file=${encodeURIComponent(
				`${window.origin}${fileUrl}`
			)}`,
		[fileUrl]
	)

	useEffect(() => {
		if (iframeRef.current) setIframeRef(iframeRef.current)
	}, [setIframeRef])

	useEffect(() => {
		const iframe = iframeRef.current
		if (!iframe) return

		const onLoad = () => {
			const doc = iframe.contentDocument
			if (!doc) return

			doc.documentElement.classList.toggle(
				'dark',
				resolvedTheme === 'dark'
			)

			if (!doc.getElementById('primer-pdf-bridge')) {
				const link = doc.createElement('link')
				link.id = 'primer-pdf-bridge'
				link.rel = 'stylesheet'
				link.href = pdfBridgeCssUrl
				doc.head.appendChild(link)
			}

			if (!doc.getElementById('primer-scroll-js')) {
				const s = doc.createElement('script')
				s.type = 'module'
				s.id = 'primer-scroll-js'
				s.src = scrollHandlerJsUrl
				doc.body.appendChild(s)
			}
		}

		iframe.addEventListener('load', onLoad)
		return () => iframe.removeEventListener('load', onLoad)
	}, [fileUrl, resolvedTheme])

	useEffect(() => {
		const doc = iframeRef.current?.contentDocument
		if (doc)
			doc.documentElement.classList.toggle(
				'dark',
				resolvedTheme === 'dark'
			)
	}, [resolvedTheme])

	return (
		<iframe
			ref={iframeRef}
			src={viewerSrc}
			className='w-full h-full border-none'
			title='PDF Viewer'
		/>
	)
}
