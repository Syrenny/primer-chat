import { Button } from '@/components/ui/button'
import { chatMetaStore } from '@/stores/chatmeta'
import { MessageSquarePlus } from 'lucide-react'
import { useStore } from 'zustand'
import { useChatNavigation } from '../hooks/useChatNavigation'

export default function CreateChatButton() {
	const createChat = useStore(chatMetaStore, state => state.createChat)
	const { goToChat } = useChatNavigation()
	const handleCreateChat = async () => {
		const response = await createChat([])
		if (response) {
			const historyId = response.history_id
			goToChat(historyId)
		}
	}

	return (
		<Button
			className='w-full justify-start h-12'
			variant='ghost'
			onClick={handleCreateChat}
		>
			<MessageSquarePlus className='ml-4 w-4 h-4' /> Новый чат
		</Button>
	)
}
