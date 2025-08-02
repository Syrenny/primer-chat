// components/modals/FilesModal.tsx
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import {
	Dialog,
	DialogClose,
	DialogContent,
	DialogFooter,
	DialogHeader,
	DialogTitle,
} from '@/components/ui/dialog'
import { ScrollArea } from '@/components/ui/scroll-area'
import { fileStore } from '@/stores/files'
import { uiStore } from '@/stores/ui'
import { Info, Trash2, Upload } from 'lucide-react'
import { useEffect } from 'react'
import { useStore } from 'zustand'

export default function FilesModal() {
	const isOpen = useStore(uiStore, s => s.isFilesModalOpen)
	const closeModal = useStore(uiStore, s => s.closeFilesModal)

	const files = useStore(fileStore, s => s.files)
	const fetchFiles = useStore(fileStore, s => s.fetchFiles)
	const deleteFile = useStore(fileStore, s => s.deleteFile)
	const uploadFile = useStore(fileStore, s => s.uploadFile)

	useEffect(() => {
		if (isOpen) fetchFiles()
	}, [isOpen, fetchFiles])

	const handleUpload = async () => {
		const input = document.createElement('input')
		input.type = 'file'
		input.accept = '.pdf'
		input.onchange = async () => {
			const file = input.files?.[0]
			if (file) {
				await uploadFile(file)
				await fetchFiles()
			}
		}
		input.click()
	}

	return (
		<Dialog open={isOpen} onOpenChange={open => !open && closeModal()}>
			<DialogContent className='max-w-2xl'>
				<DialogHeader>
					<DialogTitle>Мои файлы</DialogTitle>
				</DialogHeader>

				<div className='space-y-4'>
					<Button variant='secondary' onClick={handleUpload}>
						<Upload className='mr-2 w-4 h-4' /> Загрузить файл
					</Button>

					<Alert>
						<Info className='h-4 w-4' />
						<AlertTitle className=''>Ограничения</AlertTitle>
						<AlertDescription className='space-y-2'>
							<ul className='list-inside list-disc text-sm'>
								<li>
									Поддерживаются файлы в формате{' '}
									<b>.pdf</b>.
								</li>
								<li>
									Максимальное количество файлов: <b>10</b>.
								</li>
								<li>
									Названия файлов <b>не должны повторяться</b>
									.
								</li>
							</ul>
						</AlertDescription>
					</Alert>

					<ScrollArea className='max-h-[50vh] border rounded-md p-2'>
						{files.length === 0 ? (
							<p className='text-muted-foreground text-sm'>
								Нет загруженных файлов
							</p>
						) : (
							<ul className='space-y-2'>
								{files.map(file => (
									<li
										key={file.file_id}
										className='flex items-center justify-between'
									>
										<span className='truncate max-w-[80%]'>
											{file.filename}
										</span>
										<Button
											variant='ghost'
											size='icon'
											onClick={() =>
												deleteFile(file.file_id).then(
													fetchFiles
												)
											}
											title='Удалить файл'
										>
											<Trash2 className='w-4 h-4 text-destructive' />
										</Button>
									</li>
								))}
							</ul>
						)}
					</ScrollArea>
				</div>

				<DialogFooter className='mt-4'>
					<DialogClose asChild>
						<Button variant='secondary'>Закрыть</Button>
					</DialogClose>
				</DialogFooter>
			</DialogContent>
		</Dialog>
	)
}
