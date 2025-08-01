import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { chatMetaStore } from '@/stores/chatmeta'
import { fileStore } from '@/stores/files'
import { Plus, Trash2, Upload } from 'lucide-react'
import { useEffect, useState } from 'react'
import { toast } from 'react-toastify'
import { useStore } from 'zustand'

export default function FileSection() {
	// File store
	const files = useStore(fileStore, state => state.files)
	const fetchFiles = useStore(fileStore, state => state.fetchFiles)
	const deleteFile = useStore(fileStore, state => state.deleteFile)
	const uploadFile = useStore(fileStore, state => state.uploadFile)

	// ChatMeta store
	const chats = useStore(chatMetaStore, state => state.chats)
	const updateChat = useStore(chatMetaStore, state => state.updateChat)
	const createChat = useStore(chatMetaStore, state => state.createChat)
	const fetchChats = useStore(chatMetaStore, state => state.fetchChats)

	const [selectedChatId, setSelectedChatId] = useState<string | null>(null)

	useEffect(() => {
		fetchFiles()
	}, [])

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

	const handleAddFileToChat = async (fileId: string) => {
		if (!selectedChatId) {
			const newChat = await createChat([fileId])
			if (!newChat) return toast.error('Failed to add file')
			setSelectedChatId(newChat.history_id)
			await fetchChats()
			return
		}

		const chat = chats.find(c => c.history_id === selectedChatId)
		if (!chat) return

		const fileIds = chat.files.map(f => f.file_id)
		if (!fileIds.includes(fileId)) {
			await updateChat(selectedChatId, [...fileIds, fileId])
			await fetchChats()
		}
	}

	const handleDeleteFile = async (fileId: string) => {
		await deleteFile(fileId)
		await fetchFiles()
	}

	return (
		<div className='h-[30%] overflow-auto'>
			<h3 className='text-md font-normal px-4 pt-4 pb-2 text-muted-foreground select-none'>
				Файлы
			</h3>
			<div className='flex px-3 mb-3'>
				<Button
					className='w-full h-11 justify-start'
					variant='ghost'
					onClick={handleUpload}
				>
					<Upload className='mx-2' /> Загрузить файл
				</Button>
			</div>
			<ScrollArea className='px-4 pb-4'>
				{files.map(file => (
					<div
						key={file.file_id}
						className='flex justify-between items-center mb-2'
					>
						<span
							title={file.filename}
							className='truncate block max-w-full contain-inline-size flex-1 select-none'
						>
							{file.filename}
						</span>
						<div className='flex gap-1'>
							<Button
								variant='ghost'
								size='icon'
								title='Добавить в чат'
								onClick={() =>
									handleAddFileToChat(file.file_id)
								}
							>
								<Plus className='w-4 h-4' />
							</Button>
							<Button
								variant='ghost'
								size='icon'
								title='Удалить'
								onClick={() => handleDeleteFile(file.file_id)}
							>
								<Trash2 className='w-4 h-4 text-destructive' />
							</Button>
						</div>
					</div>
				))}
			</ScrollArea>
		</div>
	)
}
