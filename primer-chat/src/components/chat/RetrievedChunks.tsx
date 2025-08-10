import { pdfViewerStore } from '@/stores/pdfViewer'
import type { IndexedChunk } from '@/types/chunks'
import { useStore } from 'zustand'

interface RetrievedChunksProps {
	chunks: IndexedChunk[]
}

export function RetrievedChunks({ chunks }: RetrievedChunksProps) {
	if (!chunks.length) return null

	const highlightPositions = useStore(
		pdfViewerStore,
		s => s.highlightPositions
	)

	const handleClick = async (index: number) => {
		highlightPositions(chunks[index].positions)
	}

	return (
		<div className='mt-4 space-y-2 text-sm '>
			<div className='text-xs text-muted-foreground font-medium uppercase tracking-wide px-1'>
				Использованные фрагменты
			</div>
			<ul className='space-y-1 border-l-1 border-primary pl-3'>
				{chunks.map((chunk, idx) => (
					<li key={idx}>
						<button
							type='button'
							onClick={() => handleClick(idx)}
							className='flex items-center w-full text-left text-primary hover:underline hover:text-primary/90 transition-colors max-w-xs hover:cursor-pointer'
						>
							<span className='truncate flex-1'>
								{chunk.filename} (стр. {chunk.positions[0].page}
								)
							</span>
						</button>
					</li>
				))}
			</ul>
		</div>
	)
}
