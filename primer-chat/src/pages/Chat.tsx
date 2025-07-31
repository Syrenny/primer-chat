import LeftSidebar from '@/components/LeftSidebar'
import { ScrollArea } from '@/components/ui/scroll-area'
import { useGenerationStore } from '@/stores/generation'
import { useHistoryStore } from '@/stores/history'
import { useLayoutEffect, useRef } from 'react'
import { useParams } from 'react-router-dom'
import 'react-toastify/dist/ReactToastify.css'
import ChatContent from '../components/chat/ChatContent'
import ChatInput from '../components/chat/ChatInput'
import Header from '../components/Header'

const Chat = () => {
	const chatEndRef = useRef<HTMLDivElement | null>(null)
	const { messages, addUserMessage, updateAssistantMessage } =
		useHistoryStore()
	const { isWaitingForGeneration, isGenerating, startGeneration } =
		useGenerationStore()
	const { history_id } = useParams()

	useLayoutEffect(() => {
		chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
	}, [messages])

	const handleSendMessage = async (input: string) => {
		if (
			!input.trim() ||
			isGenerating ||
			isWaitingForGeneration ||
			history_id === undefined
		)
			return

		addUserMessage(input)

		await startGeneration(input, history_id, {
			onData: updateAssistantMessage,
		})
	}

	return (
		<div className='flex flex-row h-full w-screen overflow-hidden'>
			<LeftSidebar />

			<div className='flex flex-col w-full'>
				<Header />

				<div className='flex flex-col flex-1 items-center justify-between overflow-hidden'>
					<ScrollArea className='relative bottom-1 overflow-y-auto w-full'>
						<div className='w-full flex flex-col justify-center items-center'>
							{history_id && (
								<div className='w-full max-w-3xl'>
									<ChatContent history_id={history_id} />
								</div>
							)}
						</div>

						<div ref={chatEndRef} />
					</ScrollArea>

					<div
						className='relative bottom-3 w-full shrink-0 bg-transparent'
						style={{
							maxWidth: 'min(97%, 48rem)',
						}}
					>
						<ChatInput onSubmit={handleSendMessage} />
					</div>
				</div>
			</div>
		</div>
	)
}

export default Chat
