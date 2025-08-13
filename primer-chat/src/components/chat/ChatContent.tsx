import { Alert, AlertDescription } from '@/components/ui/alert'
import { generationStore } from '@/stores/generation'
import { historyStore } from '@/stores/history'
import { AlertTriangle } from 'lucide-react'
import { useEffect, useLayoutEffect, useRef, useState } from 'react'
import { useStore } from 'zustand'
import { ScrollArea, ScrollBar } from '../ui/scroll-area'
import AssistantMessage from './AssistantMessage'
import { ChatIntroduction } from './ChatIntroduction'
import UserMessage from './UserMessage'

import GeneratingMessage from './GeneratingMessage'

interface ChatContentProps {
	historyId: string | undefined
}

const ChatContent = ({ historyId }: ChatContentProps) => {
	const requests = useStore(historyStore, s => s.requests)
	const isHistoryLoading = useStore(historyStore, s => s.isHistoryLoading)
	const loadHistory = useStore(historyStore, s => s.loadHistory)

	const isWaitingForGeneration = useStore(
		generationStore,
		s => s.isWaitingForGeneration
	)
	const isGenerating = useStore(generationStore, s => s.isGenerating)
	const chatEndRef = useRef<HTMLDivElement | null>(null)

	const [error, setError] = useState<string | null>(null)

	useLayoutEffect(() => {
		chatEndRef.current?.scrollIntoView({ behavior: 'auto' })
	}, [requests])

	// Автоскролл при смене статуса генерации
	useEffect(() => {
		if (isWaitingForGeneration || isGenerating) {
			chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
		}
	}, [isWaitingForGeneration, isGenerating])

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
			<div className='w-full p-4'>
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

	const showGenerating = isWaitingForGeneration || isGenerating
	const phase: 'pre' | 'stream' = isWaitingForGeneration ? 'pre' : 'stream'

	return (
		<ScrollArea
			className='flex h-full w-full flex-1 overflow-y-auto'
			aria-busy={showGenerating ? true : undefined}
		>
			<div className='flex h-full w-full flex-col items-center justify-center'>
				<div className='h-full w-full max-w-3xl'>
					<div className='flex w-full flex-col space-y-8 px-3 pt-6 pb-24'>
						{requests.map(req => (
							<div
								key={req.requestId}
								className='flex flex-col gap-y-4'
							>
								<UserMessage
									key={`user_${req.requestId}`}
									request={req}
								/>
								<AssistantMessage
									key={`assistant_${req.requestId}`}
									request={req}
								/>
							</div>
						))}

						{/* 👇 вместо маленького Skeleton — полноценный «ассистент печатает» */}
						{showGenerating && <GeneratingMessage phase={phase} />}

						<div ref={chatEndRef} />
					</div>
				</div>
			</div>

			<ScrollBar orientation='vertical' />
		</ScrollArea>
	)
}

export default ChatContent
