import ChatWindow from '@/components/chat/ChatWindow'
import Header from '@/components/Header'
import LeftSidebar from '@/components/LeftSidebar'
import FilesModal from '@/components/modal/FilesModal'
import PDFViewer from '@/components/pdf-viewer/PdfViewer'
import {
	ResizableHandle,
	ResizablePanel,
	ResizablePanelGroup,
} from '@/components/ui/resizable'
import { historyStore } from '@/stores/history'
import { layoutStore } from '@/stores/layoutPanels'
import { useLayoutEffect, useRef } from 'react'
import { useParams } from 'react-router-dom'
import 'react-toastify/dist/ReactToastify.css'
import { useStore } from 'zustand'

const Chat = () => {
	const panelSizes = useStore(layoutStore, s => s.panelSizes)
	const setPanelSizes = useStore(layoutStore, s => s.setPanelSizes)
	const chatEndRef = useRef<HTMLDivElement | null>(null)

	// History store
	const requests = useStore(historyStore, state => state.requests)

	const { fileId } = useParams()

	useLayoutEffect(() => {
		chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
	}, [requests])

	return (
		<div className='flex flex-row h-dvh'>
			<FilesModal />
			<LeftSidebar />
			<div className='flex flex-col h-full w-full'>
				<Header />
				<ResizablePanelGroup
					direction='horizontal'
					onLayout={setPanelSizes}
				>
					<ResizablePanel
						id='pdf-panel'
						defaultSize={panelSizes[0]}
						className='min-w-xs'
					>
						<PDFViewer fileId={fileId} />
					</ResizablePanel>
					<ResizableHandle withHandle />
					<ResizablePanel
						id='chat-panel'
						className='min-w-sm'
						defaultSize={panelSizes[1]}
					>
						<ChatWindow />
					</ResizablePanel>
				</ResizablePanelGroup>
			</div>
		</div>
	)
}

export default Chat
