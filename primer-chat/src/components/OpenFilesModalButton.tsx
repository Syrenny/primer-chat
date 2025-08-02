import { Button } from '@/components/ui/button'
import { uiStore } from '@/stores/ui'
import { useStore } from 'zustand'
import { FileText } from 'lucide-react'

export function OpenFilesModalButton() {
	const open = useStore(uiStore, s => s.openFilesModal)

	return (
        <Button
			className='w-full h-11 justify-start'
			variant='ghost'
			onClick={open}
		>
			<FileText className='ml-2 w-6 h-6' /> Мои файлы
		</Button>
	)
}
