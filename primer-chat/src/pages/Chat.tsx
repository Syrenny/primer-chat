import LeftSidebar from '@/components/LeftSidebar'
import { useGenerationStore } from '@/stores/generation'
import { useHistoryStore } from '@/stores/history'
import { useLayoutEffect, useRef } from 'react'
import { useParams } from 'react-router-dom'
import 'react-toastify/dist/ReactToastify.css'
import ChatContent from '../components/chat/ChatContent'
import ChatInput from '../components/chat/ChatInput'
import Header from '../components/Header'

const Chat = () => {
	const chatContainerRef = useRef<HTMLDivElement | null>(null)
	const { messages, addUserMessage, updateAssistantMessage } =
		useHistoryStore()
	const { isWaitingForGeneration, isGenerating, startGeneration } =
		useGenerationStore()
	const { history_id } = useParams()

	useLayoutEffect(() => {
		scrollToBottom()
	}, [messages])

	const scrollToBottom = () => {
		if (chatContainerRef.current) {
			requestAnimationFrame(() => {
				if (chatContainerRef.current) {
					chatContainerRef.current.scrollTop =
						chatContainerRef.current.scrollHeight
				}
			})
		}
	}

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
		<div className='flex flex-col h-full w-full'>
			<Header />
			<div className='h-full w-full flex flex-row'>
				<LeftSidebar />
				<div className='h-full flex-1 w-full flex flex-col justify-center items-center'>
					<div
						ref={chatContainerRef}
						className='flex-1 overflow-y-scroll flex justify-center w-full'
					>
						{history_id && (
							<div className='w-full max-w-3xl max-sm:max-w-[95%]'>
								<ChatContent history_id={history_id} />
							</div>
						)}
					</div>

					<div
						className='flex mx-auto mb-8 w-full'
						style={{ maxWidth: 'min(95%, 48rem)' }}
					>
						<ChatInput onSubmit={handleSendMessage} />
					</div>
				</div>
			</div>
		</div>
	)
}

export default Chat
