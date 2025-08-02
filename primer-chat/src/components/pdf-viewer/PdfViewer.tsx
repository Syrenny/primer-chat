import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { ScrollArea, ScrollBar } from '@/components/ui/scroll-area'
import { Skeleton } from '@/components/ui/skeleton'
import { fileStore } from '@/stores/files'
import { uiStore } from '@/stores/ui'
import { AlertTriangle, Menu, Minus, Plus } from 'lucide-react'
import * as pdfjsLib from 'pdfjs-dist'
import { useEffect, useRef, useState } from 'react'
import { useStore } from 'zustand'

// 👇 Устанавливаем воркер
pdfjsLib.GlobalWorkerOptions.workerSrc =
	window.location.origin + '/pdf.worker.min.mjs'

interface PDFViewerProps {
	fileId?: string // теперь необязательный
}

export default function PDFViewer({ fileId }: PDFViewerProps) {
	const getFileLink = useStore(fileStore, s => s.getFileLink)
	const [fileUrl, setFileUrl] = useState<string | null>(null)
	const [pdf, setPdf] = useState<pdfjsLib.PDFDocumentProxy | null>(null)
	const [scale, setScale] = useState(1.25)
	const [pageCount, setPageCount] = useState(0)
	const [error, setError] = useState<string | null>(null)

	useEffect(() => {
		if (!fileId) {
			setError('Файл не выбран. Пожалуйста, выберете файл в меню слева.')
			return
		}

		const fetchLink = async () => {
			try {
				const link = await getFileLink(fileId)
				if (link) {
					setFileUrl(link.url.toString())
					setError(null)
				} else {
					setError('Не удалось получить ссылку на файл.')
				}
			} catch (err) {
				console.error(err)
				setError('Произошла ошибка при получении файла.')
			}
		}
		fetchLink()
	}, [fileId, getFileLink])

	useEffect(() => {
		if (!fileUrl) return
		const load = async () => {
			try {
				const doc = await pdfjsLib.getDocument(fileUrl).promise
				setPdf(doc)
				setPageCount(doc.numPages)
				setError(null)
			} catch (err) {
				console.error(err)
				setError('Ошибка при загрузке PDF-файла.')
			}
		}
		load()
	}, [fileUrl])

	return (
		<div className='flex flex-col space-y-2 w-full h-dvh'>
			<div className='relative top-0 h-15 shrink-0 flex items-center justify-start px-2 border-b border-border'>
				<div className='mr-8'>
					<SidebarToggleButton />
				</div>
				<div className='flex flex-col mr-auto flex-1'>
					<span className='text-xl font-semibold text-foreground tracking-tight contain-inline-size flex-1 truncate'>
						Primer Chat
					</span>
					<span className='text-xs text-muted-foreground tracking-wide contain-inline-size flex-1 truncate'>
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

			{/* Контент */}
			<ScrollArea className='h-full w-full pr-2 overflow-auto '>
				<div className='flex flex-col flex-1 items-center'>
					{error ? (
						<Alert variant='default'>
							<AlertTriangle className='h-4 w-4' />
							<AlertDescription>{error}</AlertDescription>
						</Alert>
					) : pdf && pageCount > 0 ? (
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

				<ScrollBar orientation='horizontal' className='h-5' />
			</ScrollArea>
		</div>
	)
}

function SidebarToggleButton() {
	const toggleSidebar = useStore(uiStore, s => s.toggleSidebar)
	return (
		<Button variant='ghost' size='icon' onClick={toggleSidebar}>
			<Menu className='w-5 h-5' />
		</Button>
	)
}

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
		<div className='w-fit h-fit px-26 my-4'>
			<canvas ref={canvasRef} />
			<div className='text-center text-sm text-muted-foreground mt-2'>
				Стр. {pageNumber}
			</div>
		</div>
	)
}
