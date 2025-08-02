import ChatWindow from '@/components/chat/ChatWindow'
import LeftSidebar from '@/components/LeftSidebar'
import FilesModal from '@/components/modal/FilesModal'
import PDFViewer from '@/components/pdf-viewer/PdfViewer'
import { generationStore } from '@/stores/generation'
import { historyStore } from '@/stores/history'
import { useLayoutEffect, useRef } from 'react'
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels'
import { useParams } from 'react-router-dom'
import 'react-toastify/dist/ReactToastify.css'
import { useStore } from 'zustand'
const Chat = () => {
	const chatEndRef = useRef<HTMLDivElement | null>(null)

	// History store
	const messages = useStore(historyStore, state => state.messages)
	const addUserMessage = useStore(historyStore, state => state.addUserMessage)
	const updateAssistantMessage = useStore(
		historyStore,
		state => state.updateAssistantMessage
	)

	// Generation store
	const isGenerating = useStore(generationStore, state => state.isGenerating)
	const isWaitingForGeneration = useStore(
		generationStore,
		state => state.isWaitingForGeneration
	)
	const startGeneration = useStore(
		generationStore,
		state => state.startGeneration
	)

	const { historyId, fileId } = useParams()

	useLayoutEffect(() => {
		chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
	}, [messages])

	const handleSendMessage = async (input: string) => {
		if (
			!input.trim() ||
			isGenerating ||
			isWaitingForGeneration ||
			historyId === undefined
		)
			return

		addUserMessage(input)

		await startGeneration(input, historyId, {
			onData: updateAssistantMessage,
		})
	}

	return (
		<div className='flex flex-row h-dvh'>
			<FilesModal />
			<LeftSidebar />
			<PanelGroup direction='horizontal'>
				<Panel id='pdf-panel' minSize={30}>
					<PDFViewer fileId={fileId} />
				</Panel>
				<PanelResizeHandle className='w-1 bg-muted' />
				<Panel
					id='chat-panel'
					className='h-dvh flex flex-col'
					minSize={30}
				>
					<ChatWindow />
				</Panel>
			</PanelGroup>
		</div>
	)
}

export default Chat
