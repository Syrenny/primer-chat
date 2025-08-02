// components/pdf-viewer/PdfViewer.tsx
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { fileStore } from '@/stores/files'
import { uiStore } from '@/stores/ui'
import { AlertTriangle, Menu } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useStore } from 'zustand'
import { PDFViewerEmbed } from './PdfViewerEmbed'

interface PDFViewerProps {
	fileId?: string
}

export default function PDFViewer({ fileId }: PDFViewerProps) {
	const getFileLink = useStore(fileStore, s => s.getFileLink)
	const toggleSidebar = useStore(uiStore, s => s.toggleSidebar)

	const [fileUrl, setFileUrl] = useState<string | null>(null)
	const [error, setError] = useState<string | null>(null)

	useEffect(() => {
		if (!fileId) {
			setError('Файл не выбран. Пожалуйста, выберите файл в меню слева.')
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
	}, [fileId])

	return (
		<div className='flex flex-col h-dvh w-full'>
			<div className='h-15 shrink-0 flex items-center justify-between px-4 border-b border-border bg-background'>
				<Button variant='ghost' size='icon' onClick={toggleSidebar}>
					<Menu className='w-5 h-5' />
				</Button>
				<div className='flex flex-col flex-1 mx-4 truncate'>
					<span className='text-xl font-semibold text-foreground truncate'>
						Primer Chat
					</span>
					<span className='text-xs text-muted-foreground truncate'>
						Developed for JMLC (AI Talent Hub)
					</span>
				</div>
			</div>

			{error ? (
				<div className='flex-1 flex justify-center items-center p-4'>
					<Alert variant='default'>
						<AlertTriangle className='h-4 w-4' />
						<AlertDescription>{error}</AlertDescription>
					</Alert>
				</div>
			) : fileUrl ? (
				<PDFViewerEmbed fileUrl={fileUrl} />
			) : (
				<div className='flex-1'>
					<Skeleton className='w-full h-full' />
				</div>
			)}
		</div>
	)
}
