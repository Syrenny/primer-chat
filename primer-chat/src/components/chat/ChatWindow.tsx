import { generationStore } from '@/stores/generation'
import { useParams } from 'react-router-dom'
import { useStore } from 'zustand'
import ChatContent from './ChatContent'
import ChatInput from './ChatInput'

export default function ChatWindow() {
	const { historyId } = useParams()

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

		await startGeneration(input, historyId, {})
	}

	return (
		<div className='relative flex flex-col flex-1 items-center justify-between w-full h-full pb-15 px-4'>
			<ChatContent historyId={historyId} />

			<div className='absolute bottom-6 w-full  max-w-[48rem] px-5'>
				<ChatInput onSubmit={handleSendMessage} />
			</div>
		</div>
	)
}
