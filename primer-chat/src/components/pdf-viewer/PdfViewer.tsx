import { Button } from '@/components/ui/button'
import { ScrollArea, ScrollBar } from '@/components/ui/scroll-area'
import { Skeleton } from '@/components/ui/skeleton'
import { fileStore } from '@/stores/files'
import { Minus, Plus } from 'lucide-react'
import * as pdfjsLib from 'pdfjs-dist'
import { useEffect, useRef, useState } from 'react'
import { useStore } from 'zustand'
import { Menu } from 'lucide-react'
import { uiStore } from '@/stores/ui'
export function SidebarToggleButton() {
	const toggleSidebar = useStore(uiStore, s => s.toggleSidebar)

	return (
		<Button variant='ghost' size='icon' onClick={toggleSidebar}>
			<Menu className='w-5 h-5' />
		</Button>
	)
}

// 👇 Устанавливаем воркер для pdf.js
pdfjsLib.GlobalWorkerOptions.workerSrc =
	window.location.origin + '/pdf.worker.min.mjs'

interface PDFViewerProps {
	fileId: string
}

export default function PDFViewer({ fileId }: PDFViewerProps) {
	const getFileLink = useStore(fileStore, s => s.getFileLink)
	const [fileUrl, setFileUrl] = useState<string | null>(null)
	const [pdf, setPdf] = useState<pdfjsLib.PDFDocumentProxy | null>(null)
	const [scale, setScale] = useState(1.25)
	const [pageCount, setPageCount] = useState(0)

	// Получаем временную ссылку
	useEffect(() => {
		const fetchLink = async () => {
			const link = await getFileLink(fileId)
			if (link) setFileUrl(link.url.toString())
		}
		fetchLink()
	}, [fileId, getFileLink])

	// Загружаем PDF-документ
	useEffect(() => {
		if (!fileUrl) return
		const load = async () => {
			const doc = await pdfjsLib.getDocument(fileUrl).promise
			setPdf(doc)
			setPageCount(doc.numPages)
		}
		load()
	}, [fileUrl])

	return (
		<div className='flex flex-col space-y-2 w-full h-dvh'>
			<div className='relative top-0 h-15 shrink-0 flex items-center justify-start px-2 border-b border-border'>
				<div className='mr-8'>
					<SidebarToggleButton />
				</div>
				<div className='flex flex-col mr-auto'>
					<span className='text-xl font-semibold text-foreground tracking-tight'>
						Primer Chat
					</span>
					<span className='text-xs text-muted-foreground tracking-wide'>
						Developed for JMLC (AI Talent Hub)
					</span>
				</div>
				<div className='flex gap-2'>
					<Button
						variant='outline'
						size='icon'
						onClick={() => setScale(s => Math.max(s - 0.25, 0.5))}
					>
						<Minus className='w-4 h-4' />
					</Button>
					<Button
						variant='outline'
						size='icon'
						onClick={() => setScale(s => Math.min(s + 0.25, 3))}
					>
						<Plus className='w-4 h-4' />
					</Button>
				</div>
			</div>

			{/* Область со всеми страницами */}
			<ScrollArea className='flex-1 overflow-y-auto px-4'>
				<div className='flex flex-col items-center py-4 gap-8'>
					{pdf && pageCount > 0 ? (
						Array.from({ length: pageCount }, (_, i) => (
							<PDFPage
								key={i}
								pageNumber={i + 1}
								pdf={pdf}
								scale={scale}
							/>
						))
					) : (
						<Skeleton className='h-full w-full' />
					)}
				</div>
				<ScrollBar orientation='vertical' />
				<ScrollBar orientation='horizontal' />
			</ScrollArea>
		</div>
	)
}

// 👇 Компонент отдельной страницы
function PDFPage({
	pdf,
	pageNumber,
	scale,
}: {
	pdf: pdfjsLib.PDFDocumentProxy
	pageNumber: number
	scale: number
}) {
	const canvasRef = useRef<HTMLCanvasElement>(null)

	useEffect(() => {
		const render = async () => {
			const page = await pdf.getPage(pageNumber)
			const viewport = page.getViewport({ scale })
			const canvas = canvasRef.current
			if (!canvas) return

			const context = canvas.getContext('2d')
			if (!context) return

			canvas.height = viewport.height
			canvas.width = viewport.width

			await page.render({
				canvasContext: context,
				viewport: viewport,
				canvas,
			}).promise
		}
		render()
	}, [pdf, pageNumber, scale])

	return (
		<div >
			<canvas ref={canvasRef} className='' />
			<div className='text-center text-sm text-muted-foreground mt-1'>
				Стр. {pageNumber}
			</div>
		</div>
	)
}
