import { type ClientChatRequest } from '../../types/chat'
import MarkdownRenderer from './markdown/MarkdownRenderer'
import { RetrievedChunks } from './RetrievedChunks'

interface ChatMessageProps {
	request: ClientChatRequest
}


const AssistantMessage = ({ request }: ChatMessageProps) => {
	return (
		request.assistantMessage && (
			<div className='w-full flex flex-col h-full'>
				<MarkdownRenderer content={request.assistantMessage.content} />
				<RetrievedChunks key={`chunks_${request.requestId}`} chunks={request.chunks} />
			</div>
		)
	)
}

export default AssistantMessage
