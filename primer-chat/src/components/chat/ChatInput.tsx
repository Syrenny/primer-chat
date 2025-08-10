// ChatInput.tsx
import { Button } from '@/components/ui/button'
import { ScrollArea, ScrollBar } from '@/components/ui/scroll-area'
import { generationStore } from '@/stores/generation'
import clsx from 'clsx'
import { ArrowUp, Loader2 } from 'lucide-react'
import React, { useEffect, useRef, useState } from 'react'
import { useStore } from 'zustand'

type ChatInputProps = {
	onSubmit: (input: string) => void
	maxRows?: number
}

const ChatInput: React.FC<ChatInputProps> = ({ onSubmit, maxRows = 6 }) => {
	const lineHeight = 24
	const maxPx = lineHeight * (maxRows ?? 6)
	const scrollAreaRef = useRef<HTMLDivElement>(null)

	const [message, setMessage] = useState('')
	const [isComposing, setIsComposing] = useState(false)

	const isWaitingForGeneration = useStore(
		generationStore,
		s => s.isWaitingForGeneration
	)
	const isGenerating = useStore(generationStore, s => s.isGenerating)
	const isBusy = isWaitingForGeneration || isGenerating

	const inputRef = useRef<HTMLDivElement>(null)
	const containerRef = useRef<HTMLDivElement>(null)

	const readText = () =>
		(inputRef.current?.innerText ?? '').replace(/\u00A0/g, ' ') // nbsp → space

	const adjustHeight = () => {
		const el = inputRef.current
		const root = scrollAreaRef.current
		if (!el || !root) return

		// Сначала сбрасываем, чтобы scrollHeight измерился честно
		el.style.height = 'auto'
		// Контент в contenteditable может раскладываться на div/p — используем scrollHeight
		const content = el.scrollHeight
		const next = Math.min(content, maxPx)
		root.style.height = `${next}px`
	}

	useEffect(() => {
		adjustHeight()
	}, [message])

	useEffect(() => {
		adjustHeight()
	}, [])

	const clearInput = () => {
		if (inputRef.current) {
			inputRef.current.innerText = ''
			inputRef.current.style.height = 'auto'
		}
		setMessage('')
		adjustHeight()
	}

	const handleSubmit = (e: React.KeyboardEvent | React.MouseEvent) => {
		e.preventDefault()
		const text = readText().trim()
		if (!text || isBusy) return
		onSubmit(text)
		clearInput()
	}

	const handleKeyDown = (event: React.KeyboardEvent<HTMLDivElement>) => {
		if (isComposing) return
		if (event.key === 'Enter' && !event.shiftKey) {
			event.preventDefault()
			handleSubmit(event)
		}
	}

	const handleInput = () => {
		setMessage(readText())
	}

	const handlePaste = (e: React.ClipboardEvent<HTMLDivElement>) => {
		// Паста только как plain text — исключаем форматирование и картинки
		e.preventDefault()
		const text = e.clipboardData.getData('text/plain')
		document.execCommand('insertText', false, text)
	}

	const disabled = isBusy || !message.trim()
	const placeholder = isBusy
		? 'Генерирую ответ...'
		: 'Спросите по документу...'

	return (
		<div
			ref={containerRef}
			className={clsx(
				'flex flex-row py-3 px-3 items-center w-full rounded-2xl border bg-muted/50 text-foreground shadow-sm',
				'focus-within:ring-0.5 focus-within:ring-primary/40 focus-within:border-primary/50'
			)}
		>
			<ScrollArea
				ref={scrollAreaRef}
				className='w-full pr-3'
				// Нужен relative для плацехолдера внутри
				style={{ position: 'relative' }}
			>
				{!message && (
					<span
						aria-hidden
						className='pointer-events-none text-muted-foreground'
						style={{
							position: 'absolute',
							left: 0,
							top: 0,
							lineHeight: `${lineHeight}px`,
							// соответствие minHeight ниже, чтобы визуально совпадать
							minHeight: 40,
							// небольшой отступ как у текста (шрифтовые нюансы)
							transform: 'translateY(0px)',
							whiteSpace: 'pre-wrap',
						}}
					>
						{placeholder}
					</span>
				)}

				<div
					ref={inputRef}
					role='textbox'
					aria-multiline='true'
					aria-label='Поле ввода сообщения'
					contentEditable
					suppressContentEditableWarning
					spellCheck
					style={{
						lineHeight: `${lineHeight}px`,
						height: 'auto',
						minHeight: 40,
						whiteSpace: 'pre-wrap',
						wordBreak: 'break-word',
						overflowWrap: 'anywhere',
					}}
					className={clsx(
						'w-full resize-none bg-transparent',
						'outline-none focus:outline-none focus:ring-0'
					)}
					onInput={handleInput}
					onKeyDown={handleKeyDown}
					onPaste={handlePaste}
					onCompositionStart={() => setIsComposing(true)}
					onCompositionEnd={() => setIsComposing(false)}
				/>
				<ScrollBar orientation='vertical' />
			</ScrollArea>

			<Button
				type='button'
				variant='ghost'
				size='icon'
				disabled={disabled}
				onClick={handleSubmit}
				className={clsx(
					'pointer-events-auto ml-1 my-auto mb-0 shadow-sm',
					'transition-transform active:scale-95',
					disabled
						? 'opacity-60 cursor-not-allowed'
						: 'cursor-pointer'
				)}
				aria-label={isBusy ? 'Идёт генерация' : 'Отправить'}
			>
				{isBusy ? (
					<Loader2
						className='size-5 animate-spin text-primary'
						aria-hidden='true'
					/>
				) : (
					<ArrowUp
						className='size-5 text-primary'
						aria-hidden='true'
					/>
				)}
			</Button>
		</div>
	)
}

export default ChatInput
