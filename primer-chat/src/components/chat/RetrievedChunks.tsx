interface RetrievedChunk {
	id: string
	page: number
	documentName: string
	preview: string
	onClick?: () => void
}

interface RetrievedChunksProps {
	chunks: RetrievedChunk[]
}

export function RetrievedChunks({ chunks }: RetrievedChunksProps) {
	if (!chunks.length) return null

	return (
		<div className='mt-4 space-y-2 text-sm '>
			<div className='text-xs text-muted-foreground font-medium uppercase tracking-wide px-1'>
				Использованные фрагменты
			</div>
			<ul className='space-y-1 border-l-1 border-primary pl-3'>
				{chunks.map(chunk => (
					<li key={chunk.id}>
						<button
							type='button'
							onClick={chunk.onClick}
							className='flex items-center w-full text-left text-primary hover:underline hover:text-primary/90 transition-colors max-w-xs hover:cursor-pointer'
						>
							<span className='truncate flex-1'>
								{chunk.documentName} (стр. {chunk.page})
							</span>
						</button>
					</li>
				))}
			</ul>
		</div>
	)
}
