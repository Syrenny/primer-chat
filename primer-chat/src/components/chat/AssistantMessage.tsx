import { type ClientChatMessage } from '../../types/chat'
import MarkdownRenderer from './markdown/MarkdownRenderer'


interface ChatMessageProps {
	message: ClientChatMessage
}
const AssistantMessage = ({ message }: ChatMessageProps) => {
	return (
		<div className='w-full '>
			<MarkdownRenderer content={message.data.content} />
		</div>
	)
}

export default AssistantMessage
