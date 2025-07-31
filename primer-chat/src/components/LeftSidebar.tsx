import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { Trash2, Plus } from 'lucide-react'
import { useState } from 'react'

interface Chat {
	id: string
	name: string
}

interface File {
	id: string
	name: string
}

export default function LeftSidebar() {
	const [chats, setChats] = useState<Chat[]>([
		{ id: '1', name: 'Chat 1' },
		{ id: '2', name: 'Chat 2' },
	])
	const [files, setFiles] = useState<File[]>([
		{ id: 'a', name: 'Document.pdf' },
		{ id: 'b', name: 'Notes.docx' },
	])

	const handleAddFileToChat = (fileId: string) => {
		console.log('Add file to chat:', fileId)
	}

	const handleUpload = () => {
		console.log('Upload new file')
	}

	const handleDeleteFile = (fileId: string) => {
		setFiles(files => files.filter(f => f.id !== fileId))
	}

	return (
		<aside className='w-64 h-full flex flex-col border-r bg-muted/50'>
			{/* Upload button */}
			<div className='px-1 py-4 border-b'>
				<Button className='w-full text-foreground' onClick={handleUpload}>
					Загрузить файл
				</Button>
			</div>

			{/* Chats */}
			<div className='flex-1 overflow-auto'>
				<h3 className='text-sm font-normal px-4 pt-4 pb-2 text-muted-foreground'>
					Чаты
				</h3>
				<ScrollArea className='px-1 pb-4'>
					{chats.map(chat => (
						<Button
							key={chat.id}
							variant='ghost'
							className='w-full justify-start mb-1'
						>
							{chat.name}
						</Button>
					))}
				</ScrollArea>
			</div>

			<Separator />

			{/* Files */}
			<div className='h-[40%] overflow-auto'>
				<h3 className='text-sm font-normal px-4 pt-4 pb-2 text-muted-foreground'>
					Файлы
				</h3>
				<ScrollArea className='px-4 pb-4'>
					{files.map(file => (
						<div
							key={file.id}
							className='flex justify-between items-center mb-2'
						>
							<span className='truncate text-sm'>
								{file.name}
							</span>
							<div className='flex gap-2'>
								<Button
									size='sm'
									variant='ghost'
									onClick={() => handleAddFileToChat(file.id)}
								>
									<Plus className='w-4 h-4' />
								</Button>
								<Button
									size='sm'
									variant='ghost'
									onClick={() => handleDeleteFile(file.id)}
								>
									<Trash2 className='w-4 h-4 text-red-500' />
								</Button>
							</div>
						</div>
					))}
				</ScrollArea>
			</div>
		</aside>
	)
}
