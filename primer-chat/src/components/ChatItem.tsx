import {
	AccordionContent,
	AccordionItem,
	AccordionTrigger,
} from '@/components/ui/accordion'
import { Button } from '@/components/ui/button'
import { chatMetaStore } from '@/stores/chatmeta'
import type { ApiChatMetaResponse } from '@/types/chat'
import { MinusCircle } from 'lucide-react'
import { useStore } from 'zustand'
interface ChatItemProps {
	chat: ApiChatMetaResponse
	isSelected: boolean
	onSelect: () => void
}

export default function ChatItem({
	chat,
	isSelected,
	onSelect,
}: ChatItemProps) {
	const updateChat = useStore(chatMetaStore, state => state.updateChat)
	const fetchChats = useStore(chatMetaStore, state => state.fetchChats)

	const handleRemoveFile = async (fileId: string) => {
		const fileIds = chat.files
			.filter(f => f.file_id !== fileId)
			.map(f => f.file_id)
		await updateChat(chat.history_id, fileIds)
		await fetchChats()
	}

	return (
		<AccordionItem value={chat.history_id}>
			<div className='flex items-center justify-between px-2 w-full max-w-full'>
				<Button
					variant={isSelected ? 'default' : 'ghost'}
					className='items-center justify-start h-11 flex flex-1'
					onClick={onSelect}
				>
					<span className='flex-1 contain-inline-size text-ellipsis truncate text-left'>
						{chat.files.map(f => f.filename).join(', ') ||
							'Новый чат'}
					</span>
				</Button>
				<AccordionTrigger className='hover:cursor-pointer pl-2 pr-1' title="Используемые в чате файлы"/>
			</div>

			<AccordionContent className='pr-2 '>
				<span className='italic text-sm text-muted-foreground pl-6'>
					Используемые в чате файлы:
				</span>
				<div className='pb-2 border-border border-l ml-6 pl-4'>
					{chat.files.length === 0 ? (
						<p className='text-sm text-muted-foreground'>
							Нет файлов
						</p>
					) : (
						chat.files.map(file => (
							<div
								key={file.file_id}
								className='flex justify-between items-center mb-1 w-full'
							>
								<span
									title={file.filename}
									className='truncate contain-inline-size flex-1'
								>
									{file.filename}
								</span>
								<Button
									variant='ghost'
									size='icon'
									title='Удалить файл из чата'
									onClick={() =>
										handleRemoveFile(file.file_id)
									}
								>
									<MinusCircle className='w-8 h-8 text-destructive' />
								</Button>
							</div>
						))
					)}
				</div>
			</AccordionContent>
		</AccordionItem>
	)
}
