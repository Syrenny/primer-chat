import { Button } from '@/components/ui/button'
import { useGenerationStore } from '@/stores/generation'
import { ArrowRight } from 'lucide-react'
import React, { useRef, useState } from 'react'

type ChatInputProps = {
	onSubmit: (input: string) => void
}

const ChatInput: React.FC<ChatInputProps> = ({ onSubmit }) => {
	const [message, setMessage] = useState('')
	const { isWaitingForGeneration, isGenerating } = useGenerationStore()
	const textareaRef = useRef<HTMLTextAreaElement>(null)

	const handleSubmit = (e: React.KeyboardEvent | React.MouseEvent) => {
		e.preventDefault()
		if (!message.trim() || isWaitingForGeneration || isGenerating) return
		setMessage('')
		onSubmit(message)
		if (textareaRef.current) {
			textareaRef.current.style.height = 'auto'
		}
	}

	const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
		setMessage(e.target.value)

		const textarea = textareaRef.current
		if (textarea) {
			textarea.style.height = 'auto'
			textarea.style.height = `${Math.min(
				textarea.scrollHeight,
				6 * 24
			)}px`
		}
	}

	const handleKeydown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
		if (event.key === 'Enter' && !event.shiftKey) {
			event.preventDefault()
			handleSubmit(event)
		}
	}

	return (
		<div className='relative flex flex-col h-full w-full items-center rounded-4xl bg-secondary text-foreground shadow-md'>
			<div className='flex w-full flex-1 border-none bg-transparent pt-5 pb-2'>
				<div className='flex min-h-full w-full flex-col'>
					<textarea
						ref={textareaRef}
						autoFocus
						value={message}
						rows={1}
						style={{ lineHeight: '24px' }}
						className='max-h-[6lh] w-full resize-none overflow-y-auto overflow-x-hidden border-0 bg-transparent px-6 outline-none focus:ring-0 focus-visible:ring-0 text-[18px] scrollbar-thin scrollbar-thumb-gray-400 scrollbar-track-transparent dark:scrollbar-thumb-gray-600'
						onChange={handleChange}
						onKeyDown={handleKeydown}
						placeholder='Спросите что-нибудь...'
					></textarea>
				</div>
			</div>

			<div className='flex justify-end w-full h-full px-6 pb-4'>
				<Button
					variant='ghost'
					size='icon'
					className='size-8'
					disabled={
						isWaitingForGeneration ||
						isGenerating ||
						!message.trim()
					}
					onClick={handleSubmit}
				>
					<ArrowRight className='text-primary size-8' />
				</Button>
			</div>
		</div>
	)
}

export default ChatInput
