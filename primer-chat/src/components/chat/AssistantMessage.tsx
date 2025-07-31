import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { type ClientChatMessage } from '../../types/chat'

interface ChatMessageProps {
	message: ClientChatMessage
}

const AssistantMessage = ({ message }: ChatMessageProps) => {
	return (
		<div className='w-full'>
			<div className='w-full text-foreground font-sans prose prose-md prose-headings:font-semibold prose-p:leading-relaxed prose-a:text-primary dark:prose-invert prose-pre:rounded-md prose-pre:bg-muted/50 prose-code:text-sm'>
				<ReactMarkdown remarkPlugins={[remarkGfm]}>
					{message.data.content}
				</ReactMarkdown>
			</div>
		</div>
	)
}

export default AssistantMessage
