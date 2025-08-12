import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import {
	Dialog,
	DialogClose,
	DialogContent,
	DialogFooter,
	DialogHeader,
	DialogTitle,
} from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { ScrollArea } from '@/components/ui/scroll-area'
import { chatMetaStore } from '@/stores/chatmeta'
import { fileStore } from '@/stores/files'
import { uiStore } from '@/stores/ui'
import { CheckCircle2, Info, Loader2 } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import { useStore } from 'zustand'

interface AddFilesToChatModalProps {
	historyId: string
}

export default function AddFilesToChatModal({
	historyId,
}: AddFilesToChatModalProps) {
	const openChatId = useStore(uiStore, s => s.addFilesModalChatId)
	const isOpen = openChatId === historyId
	const closeModal = useStore(uiStore, s => s.closeAddFilesModal)

	const files = useStore(fileStore, s => s.files)
	const fetchFiles = useStore(fileStore, s => s.fetchFiles)
	const uploadProgress = useStore(fileStore, s => s.uploadProgress)

	const chat = useStore(chatMetaStore, s =>
		s.chats.find(c => c.history_id === historyId)
	)
	const updateChat = useStore(chatMetaStore, s => s.updateChat)
	const fetchChats = useStore(chatMetaStore, s => s.fetchChats)

	const [selectedFiles, setSelectedFiles] = useState<Set<string>>(new Set())

	useEffect(() => {
		if (isOpen) fetchFiles()
	}, [isOpen, fetchFiles])

	useEffect(() => {
		if (!isOpen) {
			setSelectedFiles(new Set())
			return
		}
		setSelectedFiles(new Set(chat?.files.map(f => f.file_id) ?? []))
	}, [isOpen, historyId, chat])

	const chatSelectedIds = useMemo(
		() => new Set(chat?.files.map(f => f.file_id) ?? []),
		[chat]
	)

	const hasChanges =
		selectedFiles.size !== chatSelectedIds.size ||
		Array.from(selectedFiles).some(id => !chatSelectedIds.has(id))

	const handleSave = async () => {
		await updateChat(historyId, Array.from(selectedFiles))
		await fetchChats()
		closeModal()
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
		<Dialog open={isOpen} onOpenChange={open => !open && closeModal()}>
			<DialogContent key={historyId} className='max-w-2xl'>
				<DialogHeader>
					<DialogTitle>Добавить файлы в чат</DialogTitle>
				</DialogHeader>

				<Alert>
					<Info className='h-4 w-4' />
					<AlertTitle>Напоминание</AlertTitle>
					<AlertDescription className='text-sm'>
						<ul className='list-inside list-disc text-sm'>
							<li>
								Новые файлы можно загрузить через меню{' '}
								<b>«Мои файлы»</b>
							</li>
							<li>
								Добавить файл в чат можно только после окончания
								индексации.
							</li>
						</ul>
					</AlertDescription>
				</Alert>

				<ScrollArea className='max-h-[50vh] border rounded-md px-4 py-2 mt-4'>
					{files.length === 0 ? (
						<p className='text-muted-foreground text-sm'>
							Нет доступных файлов
						</p>
					) : (
						<ul className='space-y-2'>
							{files.map(file => {
								const inUpload =
									typeof uploadProgress[file.file_id] ===
									'number'
								const selectable = file.is_indexed && !inUpload
								const inputId = `checkbox_${file.file_id}`
								const labelId = `label_${file.file_id}`

								return (
									<li
										key={file.file_id}
										className='flex items-center justify-between'
									>
										<Label
											id={labelId}
											htmlFor={
												selectable ? inputId : undefined
											}
											className={`w-full hover:bg-accent/50 flex items-center gap-3 rounded-lg border p-3 has-[[aria-checked=true]]:border-primary/50 hover:cursor-pointer ${
												!selectable
													? 'opacity-60 cursor-not-allowed'
													: 'cursor-pointer'
											}`}
											tabIndex={selectable ? 0 : -1}
											aria-disabled={!selectable}
											aria-checked={selectedFiles.has(
												file.file_id
											)}
										>
											<Checkbox
												id={inputId}
												checked={selectedFiles.has(
													file.file_id
												)}
												onCheckedChange={checked => {
													if (!selectable) return
													setSelectedFiles(prev => {
														const copy = new Set(
															prev
														)
														if (checked)
															copy.add(
																file.file_id
															)
														else
															copy.delete(
																file.file_id
															)
														return copy
													})
												}}
												disabled={!selectable}
											/>
											<div className='grid gap-1.5 font-normal mr-auto'>
												<p className='text-sm leading-none font-medium'>
													{file.filename}
												</p>
											</div>
											{renderStatus(
												file.file_id,
												file.is_indexed
											)}
										</Label>
									</li>
								)
							})}
						</ul>
					)}
				</ScrollArea>

				<DialogFooter className='mt-4'>
					<DialogClose asChild>
						<Button variant='secondary'>Отмена</Button>
					</DialogClose>
					<Button onClick={handleSave} disabled={!hasChanges}>
						Сохранить
					</Button>
				</DialogFooter>
			</DialogContent>
		</Dialog>
	)
}
