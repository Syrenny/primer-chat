import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { type ClientChatMessage } from '../../types/chat'

interface ChatMessageProps {
	message: ClientChatMessage
}

const AssistantMessage = ({ message }: ChatMessageProps) => {
	return (
		<div
			className='flex flex-col items-start justify-start max-w-[95%]'
			data-message-role='assistant'
			role='presentation'
		>
			<div className='w-full text-gray-800 dark:text-gray-200 break-words font-sans'>
				<div className='prose prose-p:leading-relaxed prose-p:text-[17px] dark:prose-invert prose-pre:bg-[#141414] prose-headings:font-semibold'>
					<ReactMarkdown remarkPlugins={[remarkGfm]}>
						{message.data.content}
					</ReactMarkdown>
				</div>
			</div>
		</div>
	)
}

export default AssistantMessage
