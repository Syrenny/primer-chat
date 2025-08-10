import { Alert, AlertDescription } from '@/components/ui/alert'
import { Skeleton } from '@/components/ui/skeleton'
import { generationStore } from '@/stores/generation'
import { historyStore } from '@/stores/history'
import { AlertTriangle } from 'lucide-react'
import { useEffect, useLayoutEffect, useRef, useState } from 'react'
import { useStore } from 'zustand'
import { ScrollArea, ScrollBar } from '../ui/scroll-area'
import AssistantMessage from './AssistantMessage'
import { ChatIntroduction } from './ChatIntroduction'
import UserMessage from './UserMessage'

interface ChatContentProps {
	historyId: string | undefined
}

const ChatContent = ({ historyId }: ChatContentProps) => {
	const requests = useStore(historyStore, state => state.requests)
	const isHistoryLoading = useStore(
		historyStore,
		state => state.isHistoryLoading
	)
	const loadHistory = useStore(historyStore, state => state.loadHistory)

	const isWaitingForGeneration = useStore(
		generationStore,
		state => state.isWaitingForGeneration
	)
	const chatEndRef = useRef<HTMLDivElement | null>(null)

	const [error, setError] = useState<string | null>(null)

	useLayoutEffect(() => {
		chatEndRef.current?.scrollIntoView({ behavior: 'auto' })
	}, [requests])

	useEffect(() => {
		if (!historyId) {
			setError('Пожалуйста, выберите чат в списке слева.')
			return
		}
		const load = async () => {
			try {
				await loadHistory(historyId)
				setError(null)
			} catch (err) {
				console.error(err)
				setError('Ошибка при загрузке истории чата.')
			}
		}
		load()
	}, [loadHistory, historyId])

	if (error) {
		return (
			<div className='p-4 w-full'>
				<Alert variant='default'>
					<AlertTriangle className='h-4 w-4' />
					<AlertDescription>{error}</AlertDescription>
				</Alert>
			</div>
		)
	}

	if (!isHistoryLoading && requests.length === 0) {
		return <ChatIntroduction />
	}

	return (
		<ScrollArea className='overflow-y-auto w-full flex-1 h-full flex'>
			<div className='h-full w-full flex flex-col justify-center items-center'>
				<div className='w-full max-w-3xl h-full '>
					<div className='flex flex-col w-full pt-6 pb-24 space-y-8 px-3'>
						{requests.map(req => {
							return (
								<div key={req.requestId} className='flex flex-col gap-y-4'>
									<UserMessage
										key={`user_${req.requestId}`}
										request={req}
									/>
									<AssistantMessage
										key={`assistant_${req.requestId}`}
										request={req}
									/>
								</div>
							)
						})}

						{isWaitingForGeneration && (
							<Skeleton className='h-5 w-10 mt-2' />
						)}
					</div>
				</div>
			</div>
			<div ref={chatEndRef} />
			<ScrollBar orientation='vertical' />
		</ScrollArea>
	)
}

export default ChatContent
