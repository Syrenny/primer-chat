import { Loader2 } from 'lucide-react'

type Props = { phase: 'pre' | 'stream' } // pre=ждём контекст, stream=идёт генерация

export default function GeneratingMessage({ phase }: Props) {
	const title = phase === 'pre' ? 'Подбираю контекст…' : 'Генерирую ответ…'

	return (
		<div
			role='status'
			aria-live='polite'
			aria-atomic='true'
			className='rounded-2xl border bg-muted p-3 flex items-center gap-3'
		>
			<Loader2 className='size-4 shrink-0 animate-spin text-primary' />
			<div className='space-y-2'>
				<div className='text-xs text-muted-foreground'>{title}</div>
			</div>
		</div>
	)
}
