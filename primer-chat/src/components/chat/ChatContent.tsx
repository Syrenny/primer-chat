import { Skeleton } from '@/components/ui/skeleton'
import { generationStore } from '@/stores/generation'
import { historyStore } from '@/stores/history'
import { RoleType } from '@/types/chat'
import { useEffect } from 'react'
import { useStore } from 'zustand'
import AssistantMessage from './AssistantMessage'
import { ChatIntroduction } from './ChatIntroduction'
import UserMessage from './UserMessage'

interface ChatContentProps {
	history_id: string
}

const ChatContent = ({ history_id }: ChatContentProps) => {
	const messages = useStore(historyStore, state => state.messages)
	const isHistoryLoading = useStore(
		historyStore,
		state => state.isHistoryLoading
	)
	const loadHistory = useStore(historyStore, state => state.loadHistory)

	const isWaitingForGeneration = useStore(
		generationStore,
		state => state.isWaitingForGeneration
	)

	useEffect(() => {
		loadHistory(history_id)
	}, [loadHistory, history_id])

	if (!isHistoryLoading && messages.length === 0) {
		return <ChatIntroduction />
	}

	return (
		<div className='flex flex-col w-full pt-6 pb-24 space-y-8 px-3'>
			{messages.map(msg => {
				const isUser = msg.data.role === RoleType.User
				const MessageComponent = isUser ? UserMessage : AssistantMessage
				return <MessageComponent key={msg.index} message={msg} />
			})}

			{isWaitingForGeneration && <Skeleton className='h-5 w-10 mt-2' />}
		</div>
	)
}

export default ChatContent
