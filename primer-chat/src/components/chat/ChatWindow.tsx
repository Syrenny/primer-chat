import { generationStore } from '@/stores/generation'
import { historyStore } from '@/stores/history'
import { useParams } from 'react-router-dom'
import { useStore } from 'zustand'
import ChatContent from './ChatContent'
import ChatInput from './ChatInput'

export default function ChatWindow() {
	const { historyId } = useParams()

	const addUserMessage = useStore(historyStore, s => s.addUserMessage)
	const updateAssistantMessage = useStore(
		historyStore,
		s => s.updateAssistantMessage
	)

	const isGenerating = useStore(generationStore, s => s.isGenerating)
	const isWaitingForGeneration = useStore(
		generationStore,
		s => s.isWaitingForGeneration
	)
	const startGeneration = useStore(generationStore, s => s.startGeneration)

	const handleSendMessage = async (input: string) => {
		if (
			!input.trim() ||
			isGenerating ||
			isWaitingForGeneration ||
			historyId === undefined
		)
			return

		addUserMessage(input)
		await startGeneration(input, historyId, {
			onData: updateAssistantMessage,
		})
	}

	return (
		<div className='relative flex flex-col flex-1 items-center justify-between w-full h-full pb-30'>
			<ChatContent historyId={historyId} />

			<div
				className='absolute bottom-6 w-full shrink-0 bg-transparent'
				style={{ maxWidth: 'min(97%, 48rem)' }}
			>
				<ChatInput onSubmit={handleSendMessage} />
			</div>
		</div>
	)
}
