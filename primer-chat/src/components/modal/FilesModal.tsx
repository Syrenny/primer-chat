// components/modals/FilesModal.tsx
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
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
import { chatMetaStore } from '@/stores/chatmeta'
import { fileStore } from '@/stores/files'
import { uiStore } from '@/stores/ui'
import { CheckCircle2, Info, Loader2, Trash2, Upload } from 'lucide-react'
import { useEffect } from 'react'
import { useStore } from 'zustand'

export default function FilesModal() {
	const isOpen = useStore(uiStore, s => s.isFilesModalOpen)
	const closeModal = useStore(uiStore, s => s.closeFilesModal)

	const files = useStore(fileStore, s => s.files)
	const fetchFiles = useStore(fileStore, s => s.fetchFiles)
	const deleteFile = useStore(fileStore, s => s.deleteFile)
	const uploadFile = useStore(fileStore, s => s.uploadFile)
	const uploadProgress = useStore(fileStore, s => s.uploadProgress)
	const loading = useStore(fileStore, s => s.loading)
	const error = useStore(fileStore, s => s.error)
	const refetchChats = useStore(chatMetaStore, s => s.fetchChats)

	useEffect(() => {
		if (isOpen) fetchFiles()
	}, [isOpen, fetchFiles])

	const handleUpload = async () => {
		const input = document.createElement('input')
		input.type = 'file'
		input.accept = '.pdf'
		input.multiple = true
		input.onchange = async () => {
			const selected = Array.from(input.files ?? [])
			if (selected.length === 0) return
			for (const f of selected) {
				await uploadFile(f) // можно распараллелить при желании
			}
			// fetchFiles(); // не обязателен, прогресс уже в сторе
		}
		input.click()
	}

	const renderStatus = (fileId: string, isIndexed: boolean) => {
		const p = uploadProgress[fileId] // 0..1 | undefined
		if (typeof p === 'number') {
			const pct = Math.min(100, Math.round(p * 100))
			return (
				<div className='flex items-center gap-2 text-xs text-muted-foreground'>
					<Loader2 className='size-6 animate-spin' />
					<span className='tabular-nums'>{pct}%</span>
				</div>
			)
		}
		if (!isIndexed) {
			return (
				<Badge variant='secondary' className='flex items-center gap-1'>
					<Loader2 className='size-6 animate-spin' />
					Индексация…
				</Badge>
			)
		}
		return (
			<span className='inline-flex items-center text-green-600 dark:text-green-500'>
				<CheckCircle2 className='size-6' aria-label='Готово' />
				<span className='sr-only'>Готово</span>
			</span>
		)
	}

	return (
		<Dialog
			open={isOpen}
			onOpenChange={open => {
				if (!open) {
					refetchChats()
					closeModal()
				}
			}}
		>
			<DialogContent className='max-w-2xl'>
				<DialogHeader>
					<DialogTitle>Мои файлы</DialogTitle>
				</DialogHeader>

				<div className='space-y-4'>
					<div className='flex items-center gap-2'>
						<Button
							variant='secondary'
							onClick={handleUpload}
							disabled={loading}
						>
							<Upload className='mr-2 h-4 w-4' />
							Загрузить файлы
						</Button>
					</div>

					{error && (
						<Alert variant='destructive'>
							<AlertTitle>Ошибка</AlertTitle>
							<AlertDescription className='text-sm'>
								{error}
                                Пожалуйста, попробуйте снова
							</AlertDescription>
						</Alert>
					)}

					<Alert>
						<Info className='h-4 w-4' />
						<AlertTitle>Ограничения</AlertTitle>
						<AlertDescription className='text-sm'>
							<ul className='list-inside list-disc'>
								<li>
									Поддерживаются файлы в формате <b>.pdf</b>.
								</li>
								<li>
									Максимальное количество файлов: <b>10</b>.
								</li>
							</ul>
						</AlertDescription>
					</Alert>

					<ScrollArea className='max-h-[50vh] border rounded-md px-4 py-2 mt-4'>
						{files.length === 0 ? (
							<p className='text-muted-foreground text-sm'>
								Нет загруженных файлов
							</p>
						) : (
							<ul className='space-y-2'>
								{files.map(file => {
									const inUpload =
										typeof uploadProgress[file.file_id] ===
										'number'
									return (
										<li
											key={file.file_id}
											className='flex items-center justify-between rounded-lg border p-3 hover:bg-accent/50'
										>
											<div className='min-w-0 mr-auto grid gap-1.5'>
												<p className='text-sm leading-none font-medium truncate'>
													{file.filename}
												</p>
											</div>

											<div className='ml-4 flex items-center gap-2'>
												{renderStatus(
													file.file_id,
													file.is_indexed
												)}
												<Button
													variant='ghost'
													size='icon'
													onClick={() =>
														deleteFile(
															file.file_id
														).then(fetchFiles)
													}
													title='Удалить файл'
													disabled={
														inUpload || loading
													}
												>
													<Trash2 className='h-4 w-4 text-destructive' />
												</Button>
											</div>
										</li>
									)
								})}
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
