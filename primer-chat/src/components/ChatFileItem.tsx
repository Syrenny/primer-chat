import { Button } from '@/components/ui/button'
import { MinusCircle } from 'lucide-react'
import { useChatNavigation } from '../hooks/useChatNavigation'
import { cn } from '@/lib/utils'

interface ChatFileItemProps {
	fileId: string
	historyId: string
	filename: string
	selectedHistory: boolean
	onRemove: () => void
}

export default function ChatFileItem({
	fileId,
	historyId,
	filename,
	selectedHistory,
	onRemove,
}: ChatFileItemProps) {
	const { goTo, fileId: selectedFileId } = useChatNavigation()

	return (
		<div
			className={cn(
				'flex justify-between items-center w-full border-l-4 h-11',
				selectedHistory && fileId === selectedFileId
					? 'border-primary bg-muted/50'
					: 'border-transparent'
			)}
		>
			<Button
				variant='ghost'
				className='truncate text-left flex-1 justify-start px-2 h-full'
				onClick={() => goTo(historyId, fileId)}
				title={filename}
			>
				<span className='contain-inline-size flex-1 truncate'>
					{filename}
				</span>
			</Button>
			<Button
				variant='ghost'
				size='icon'
				title='Удалить файл из чата'
				onClick={onRemove}
			>
				<MinusCircle className='w-5 h-5 text-destructive' />
			</Button>
		</div>
	)
}
