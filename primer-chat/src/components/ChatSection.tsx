import { Accordion } from '@/components/ui/accordion'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { chatMetaStore } from '@/stores/chatmeta'
import { MessageSquarePlus } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useStore } from 'zustand'
import ChatItem from './ChatItem'
import { useNavigate } from 'react-router-dom'

export default function ChatSection() {
	// ChatMeta store
	const chats = useStore(chatMetaStore, state => state.chats)
	const fetchChats = useStore(chatMetaStore, state => state.fetchChats)
    const createChat = useStore(chatMetaStore, state => state.createChat)
	const [selectedChatId, setSelectedChatId] = useState<string | null>(null)

    const navigate = useNavigate()

	useEffect(() => {
		fetchChats()
	}, [])

	const handleCreateChat = async () => {
        const response = await createChat([])
        if (response){
            const historyId = response.history_id
            navigate(`/c/${historyId}`)
            setSelectedChatId(historyId)

        }
    }

    const handleSelectChat = async (historyId: string) => {
        setSelectedChatId(historyId)
        navigate(`/c/${historyId}`)
    }

	return (
		<div className='flex-1 overflow-auto w-full'>
			<h3 className='text-md font-normal px-4 pt-4 pb-2 text-muted-foreground select-none'>
				Чаты
			</h3>
			<div className='flex px-3 mb-3'>
				<Button
					className='w-full justify-start h-11'
					variant='ghost'
					onClick={handleCreateChat}
				>
					<MessageSquarePlus className='w-4 h-4 mx-2' /> Новый чат
				</Button>
			</div>
			<ScrollArea className='pb-4 w-full'>
				<Accordion type='multiple' className='w-full'>
					{chats.map(chat => (
						<ChatItem
							key={chat.history_id}
							chat={chat}
							isSelected={chat.history_id === selectedChatId}
							onSelect={() => handleSelectChat(chat.history_id)}
						/>
					))}
				</Accordion>
			</ScrollArea>
		</div>
	)
}
