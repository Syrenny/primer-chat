import { Accordion } from '@/components/ui/accordion'
import { ScrollArea } from '@/components/ui/scroll-area'
import { chatMetaStore } from '@/stores/chatmeta'
import { useEffect } from 'react'
import { useStore } from 'zustand'
import { useChatNavigation } from '../hooks/useChatNavigation'
import ChatItem from './ChatItem'
import CreateChatButton from './CreateChatButton'
import { OpenFilesModalButton } from './OpenFilesModalButton'

export default function ChatSection() {
	// ChatMeta store
	const chats = useStore(chatMetaStore, state => state.chats)
	const fetchChats = useStore(chatMetaStore, state => state.fetchChats)

	const { goToChat } = useChatNavigation()

	useEffect(() => {
		fetchChats()
	}, [])

	const handleSelectChat = async (historyId: string) => {
		goToChat(historyId)
	}

	return (
		<div className='flex-1 overflow-auto w-full'>
			<OpenFilesModalButton />
			<CreateChatButton />
			<h3 className='text-md font-normal px-4 pt-4 pb-2 text-muted-foreground select-none'>
				Чаты
			</h3>
			<ScrollArea className='pb-4 w-full'>
				<Accordion type='multiple' className='w-full'>
					{chats.map(chat => (
						<ChatItem
							key={chat.history_id}
							chat={chat}
							onSelect={() => handleSelectChat(chat.history_id)}
						/>
					))}
				</Accordion>
			</ScrollArea>
		</div>
	)
}
