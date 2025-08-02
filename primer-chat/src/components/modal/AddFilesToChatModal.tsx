// components/modals/AddFilesToChatModal.tsx
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
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
import { ScrollArea } from '@/components/ui/scroll-area'
import { chatMetaStore } from '@/stores/chatmeta'
import { fileStore } from '@/stores/files'
import { uiStore } from '@/stores/ui'
import { Info } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useStore } from 'zustand'

interface AddFilesToChatModalProps {
	historyId: string
}

export default function AddFilesToChatModal({
	historyId,
}: AddFilesToChatModalProps) {
	const isOpen = useStore(uiStore, s => s.isAddFilesModalOpen)
	const closeModal = useStore(uiStore, s => s.closeAddFilesModal)

	const files = useStore(fileStore, s => s.files)
	const fetchFiles = useStore(fileStore, s => s.fetchFiles)

	const chat = useStore(chatMetaStore, s =>
		s.chats.find(c => c.history_id === historyId)
	)
	const updateChat = useStore(chatMetaStore, s => s.updateChat)
	const fetchChats = useStore(chatMetaStore, s => s.fetchChats)

	const [selectedFiles, setSelectedFiles] = useState<Set<string>>(new Set())

	useEffect(() => {
		if (isOpen) {
			fetchFiles()
			if (chat) {
				setSelectedFiles(new Set(chat.files.map(f => f.file_id)))
			}
		}
	}, [isOpen, chat, fetchFiles])

	const toggleFile = (fileId: string) => {
		setSelectedFiles(prev => {
			const copy = new Set(prev)
			if (copy.has(fileId)) copy.delete(fileId)
			else copy.add(fileId)
			return copy
		})
	}

	const handleSave = async () => {
		await updateChat(historyId, Array.from(selectedFiles))
		await fetchChats()
		closeModal()
	}

	return (
		<Dialog open={isOpen} onOpenChange={open => !open && closeModal()}>
			<DialogContent className='max-w-2xl'>
				<DialogHeader>
					<DialogTitle>Добавить файлы в чат</DialogTitle>
				</DialogHeader>

				<Alert>
					<Info className='h-4 w-4' />
					<AlertTitle>Напоминание</AlertTitle>
					<AlertDescription className='text-sm'>
						Новые файлы можно загрузить через меню{' '}
						<b>«Мои файлы»</b>.
					</AlertDescription>
				</Alert>

				<ScrollArea className='max-h-[50vh] border rounded-md p-2 mt-4'>
					{files.length === 0 ? (
						<p className='text-muted-foreground text-sm'>
							Нет доступных файлов
						</p>
					) : (
						<ul className='space-y-2'>
							{files.map(file => (
								<li
									key={file.file_id}
									className='flex items-center justify-between'
								>
									<div className='flex items-center gap-2'>
										<Checkbox
											checked={selectedFiles.has(
												file.file_id
											)}
											onCheckedChange={() =>
												toggleFile(file.file_id)
											}
											id={file.file_id}
										/>
										<label
											htmlFor={file.file_id}
											className='text-sm cursor-pointer truncate max-w-[70%]'
										>
											{file.filename}
										</label>
									</div>
								</li>
							))}
						</ul>
					)}
				</ScrollArea>

				<DialogFooter className='mt-4'>
					<DialogClose asChild>
						<Button variant='secondary'>Отмена</Button>
					</DialogClose>
					<Button onClick={handleSave}>Сохранить</Button>
				</DialogFooter>
			</DialogContent>
		</Dialog>
	)
}
