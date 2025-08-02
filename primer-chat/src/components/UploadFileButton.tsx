// UploadFileButton.tsx
import { Button } from '@/components/ui/button'
import { Upload } from 'lucide-react'
import { fileStore } from '@/stores/files'
import { useStore } from 'zustand'

export default function UploadFileButton() {
	const uploadFile = useStore(fileStore, state => state.uploadFile)
	const fetchFiles = useStore(fileStore, state => state.fetchFiles)

	const handleUpload = async () => {
		const input = document.createElement('input')
		input.type = 'file'
		input.accept = '.pdf'
		input.onchange = async () => {
			const file = input.files?.[0]
			if (file) {
				await uploadFile(file)
				await fetchFiles()
			}
		}
		input.click()
	}

	return (
		<Button
			className='w-full h-11 justify-start'
			variant='ghost'
			onClick={handleUpload}
		>
			<Upload className='ml-2 w-4 h-4' /> Загрузить файл
		</Button>
	)
}
