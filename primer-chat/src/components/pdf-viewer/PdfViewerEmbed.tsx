import { useTheme } from 'next-themes'

export function PDFViewerEmbed({ fileUrl }: { fileUrl: string }) {
	const { resolvedTheme } = useTheme() // resolvedTheme = 'light' | 'dark'

	const viewerSrc = `/pdfjs/web/viewer.html?file=${encodeURIComponent(
		fileUrl
	)}&theme=${resolvedTheme}`

	return (
		<iframe
			src={viewerSrc}
			className='w-full h-full border-none'
			title='PDF Viewer'
		/>
	)
}
