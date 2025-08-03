// components/pdf-viewer/PdfViewer.tsx
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Skeleton } from '@/components/ui/skeleton'
import { fileStore } from '@/stores/files'
import { AlertTriangle } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useStore } from 'zustand'
import { PDFViewerEmbed } from './PdfViewerEmbed'

interface PDFViewerProps {
	fileId?: string
}

export default function PDFViewer({ fileId }: PDFViewerProps) {
	const getFileLink = useStore(fileStore, s => s.getFileLink)

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
		<div className='flex flex-col w-full h-full'>
			{error ? (
				<div className='flex justify-start p-4'>
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
