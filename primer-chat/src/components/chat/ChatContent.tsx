import { ScrollArea } from '@/components/ui/scroll-area'
import { Skeleton } from '@/components/ui/skeleton'
import { useEffect } from 'react'
import { useGenerationStore } from '../../stores/generation'
import { useHistoryStore } from '../../stores/history'
import type { ClientChatMessage } from '../../types/chat'
import { RoleType } from '../../types/chat'
import AssistantMessage from './AssistantMessage'
import { ChatIntroduction } from './ChatIntroduction'
import UserMessage from './UserMessage'

interface ChatContentProps {
	history_id: string
}

const ChatContent = ({ history_id }: ChatContentProps) => {
	const messages = useHistoryStore(state => state.messages)
	const isHistoryLoading = useHistoryStore(state => state.isHistoryLoading)
	const loadHistory = useHistoryStore(state => state.loadHistory)

	useEffect(() => {
		loadHistory(history_id)
	}, [loadHistory])

	const { isWaitingForGeneration } = useGenerationStore()

	const is_user_message = (m: ClientChatMessage) => {
		if (m.data.role == RoleType.User) return true
		return false
	}

	return (
		<ScrollArea className='flex flex-1 flex-col w-full pb-32 pt-24 h-full'>
			<div className='mx-auto h-full w-full max-w-[95%] max-sm:max-w-[90%]'>
				{isHistoryLoading || messages.length > 0 ? (
					<>
						{messages.map(msg => {
							const isUser = is_user_message(msg)
							return (
								<div
									key={msg.index}
									className={isUser ? 'mb-3' : 'mb-6'}
								>
									{isUser ? (
										<UserMessage message={msg} />
									) : (
										<AssistantMessage message={msg} />
									)}
								</div>
							)
						})}
						{isWaitingForGeneration && (
							<Skeleton className='h-5 w-10 mt-2' />
						)}
					</>
				) : (
					<ChatIntroduction />
				)}
			</div>
		</ScrollArea>
	)
}

export default ChatContent
