import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { useChatMetaStore } from '@/stores/chatmeta'
import { useFileStore } from '@/stores/files'
import {
	MessageSquarePlus,
	MinusCircle,
	Plus,
	Trash2,
	Upload,
} from 'lucide-react'
import { useEffect, useState } from 'react'
import { toast } from 'react-toastify'

import {
	Accordion,
	AccordionContent,
	AccordionItem,
	AccordionTrigger,
} from '@/components/ui/accordion'

export default function LeftSidebar() {
	const { files, fetchFiles, deleteFile, uploadFile } = useFileStore()

	const { chats, fetchChats, deleteChat, updateChat, createChat } =
		useChatMetaStore()

	const [selectedChatId, setSelectedChatId] = useState<string | null>(null)

	useEffect(() => {
		fetchFiles()
		fetchChats()
	}, [])

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

	const handleDeleteFile = async (fileId: string) => {
		await deleteFile(fileId)
		await fetchFiles()
	}

	const handleDeleteChat = async (chatId: string) => {
		await deleteChat(chatId)
		await fetchChats()
	}

	const handleAddFileToChat = async (fileId: string) => {
		if (!selectedChatId) {
			const newChat = await createChat([fileId])
			if (newChat === null) {
				toast.error('Failed to add file')
				return
			}
			setSelectedChatId(newChat.history_id)
			await fetchChats()
			return
		}

		const chat = chats.find(c => c.history_id === selectedChatId)
		if (!chat) return

		const existingFileIds = chat.files.map(f => f.file_id)
		if (!existingFileIds.includes(fileId)) {
			await updateChat(selectedChatId, [...existingFileIds, fileId])
			await fetchChats()
		}
	}

	return (
		<aside className='w-80 h-full flex flex-col bg-sidebar border-r border-border'>
			{/* Files */}
			<div className='h-[40%] overflow-auto'>
				<h3 className='text-md font-normal px-4 pt-4 pb-2 text-muted-foreground'>
					Файлы
				</h3>

				<div className='flex px-3 mb-3'>
					<Button
						className='w-full h-11 text-lg justify-start'
						variant='default'
						onClick={handleUpload}
					>
						<Upload className='mx-2' /> Загрузить файл
					</Button>
				</div>

				<ScrollArea className='px-4 pb-4'>
					{files.map(file => (
						<div
							key={file.file_id}
							className='flex justify-between items-center mb-2'
						>
							<span
								title={file.filename}
								className='truncate text-lg not-[]:block max-w-full w-50'
							>
								{file.filename}
							</span>
							<div className='flex gap-1'>
								<Button
									variant='ghost'
									size='icon'
									title='Добавить в чат'
									onClick={() =>
										handleAddFileToChat(file.file_id)
									}
								>
									<Plus className='w-4 h-4' />
								</Button>
								<Button
									variant='ghost'
									size='icon'
									title='Удалить'
									onClick={() =>
										handleDeleteFile(file.file_id)
									}
								>
									<Trash2 className='w-4 h-4 text-destructive' />
								</Button>
							</div>
						</div>
					))}
				</ScrollArea>
			</div>

			<Separator />

			{/* Chats */}
			<div className='flex-1 overflow-auto w-full'>
				<h3 className='text-md font-normal px-4 pt-4 pb-2 text-muted-foreground'>
					Чаты
				</h3>
				<div className='flex px-3 mb-3'>
					<Button
						className='w-full text-lg justify-start h-11'
						variant='default'
						// onClick={handleUpload}
					>
						<MessageSquarePlus className='w-4 h-4 mx-2' /> Новый чат
					</Button>
				</div>
				<ScrollArea className='pb-4 w-full'>
					<Accordion type='multiple' className='w-full'>
						{chats.map(chat => (
							<AccordionItem
								key={chat.history_id}
								value={chat.history_id}
							>
								<div className='flex items-center justify-between px-2 mb-1 w-80'>
									<Button
										variant={
											chat.history_id === selectedChatId
												? 'secondary'
												: 'ghost'
										}
										className='justify-start h-11 flex w-full'
										onClick={() =>
											setSelectedChatId(chat.history_id)
										}
									>
										<span className='text-lg truncate block text-left'>
											{chat.files
												.map(f => f.filename)
												.join(', ') || 'Новый чат'}
										</span>

										<Button
											asChild={true}
											variant='ghost'
											size='sm'
										>
											<AccordionTrigger className='hover:cursor-pointer'></AccordionTrigger>
										</Button>
										{/* <Button
											variant='ghost'
											size='sm'
											title='Удалить чат'
											onClick={() =>
												handleDeleteChat(
													chat.history_id
												)
											}
										>
											<Trash2 className='w-4 h-4 text-destructive' />
										</Button> */}
									</Button>
								</div>
								<AccordionContent className='pr-2 pb-2 border-border border-l ml-6'>
									{chat.files.length === 0 ? (
										<p className='text-xs text-muted-foreground'>
											Нет файлов
										</p>
									) : (
										chat.files.map(file => (
											<div
												key={file.file_id}
												className='flex justify-end items-center mb-1 w-full '
											>
												<span className='truncate text-lg w-50'>
													{file.filename}
												</span>
												<Button
													variant='ghost'
													size='icon'
													title='Удалить файл из чата'
													onClick={async () => {
														const newFileIds =
															chat.files
																.filter(
																	f =>
																		f.file_id !==
																		file.file_id
																)
																.map(
																	f =>
																		f.file_id
																)
														await updateChat(
															chat.history_id,
															newFileIds
														)
														await fetchChats()
													}}
												>
													<MinusCircle className='w-8 h-8 text-destructive' />
												</Button>
											</div>
										))
									)}
								</AccordionContent>
							</AccordionItem>
						))}
					</Accordion>
				</ScrollArea>
			</div>
		</aside>
	)
}
