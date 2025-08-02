import {
	AccordionContent,
	AccordionItem,
	AccordionTrigger,
} from '@/components/ui/accordion'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { chatMetaStore } from '@/stores/chatmeta'
import { uiStore } from '@/stores/ui'
import type { ApiChatMetaResponse } from '@/types/chat'
import { Plus } from 'lucide-react'
import { useStore } from 'zustand'
import { useChatNavigation } from '../hooks/useChatNavigation'
import ChatFileItem from './ChatFileItem'
import AddFilesToChatModal from './modal/AddFilesToChatModal'

interface ChatItemProps {
	chat: ApiChatMetaResponse
	onSelect: () => void
}

export default function ChatItem({ chat, onSelect }: ChatItemProps) {
	// ChatMeta store
	const updateChat = useStore(chatMetaStore, s => s.updateChat)
	const fetchChats = useStore(chatMetaStore, s => s.fetchChats)

	// UI store
	const openAddFilesModal = useStore(uiStore, s => s.openAddFilesModal)

	const { historyId } = useChatNavigation()

	const isSelected = historyId === chat.history_id

	const handleRemoveFile = async (fileId: string) => {
		const updated = chat.files
			.filter(f => f.file_id !== fileId)
			.map(f => f.file_id)
		await updateChat(chat.history_id, updated)
		await fetchChats()
	}

	const handleAddFile = async () => {
		openAddFilesModal()
	}

	return (
		<AccordionItem value={chat.history_id} className='h-full w-full'>
			<AddFilesToChatModal historyId={chat.history_id} />
			<div
				className={cn(
					'flex items-center justify-between w-full max-w-full border-l-4 h-12',
					isSelected
						? 'border-primary bg-muted/50'
						: 'border-transparent'
				)}
			>
				<Button
					variant='ghost'
					className='items-center justify-start h-full flex flex-1'
					onClick={onSelect}
				>
					<span className='flex-1 contain-inline-size text-ellipsis truncate text-left'>
						{chat.files.map(f => f.filename).join(', ') ||
							'Новый чат'}
					</span>
				</Button>
				<AccordionTrigger
					className='hover:cursor-pointer pl-2 pr-1 py-0 h-full'
					title='Используемые в чате файлы'
				/>
			</div>

			<AccordionContent>
				<div className='border-border border-l ml-6 '>
					{chat.files.length > 0 &&
						chat.files.map(file => (
							<ChatFileItem
								key={file.file_id}
								fileId={file.file_id}
								historyId={chat.history_id}
								filename={file.filename}
								selectedHistory={isSelected}
								onRemove={() => handleRemoveFile(file.file_id)}
							/>
						))}
					{/* Кнопка добавить файл */}
					<Button
						variant='ghost'
						size='sm'
						className='w-full justify-start text-muted-foreground hover:text-foreground h-11'
						onClick={handleAddFile}
					>
						<Plus className='w-4 h-4' /> Добавить файл
					</Button>
				</div>
			</AccordionContent>
		</AccordionItem>
	)
}
