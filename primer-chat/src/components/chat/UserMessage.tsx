import { type ClientChatRequest } from '../../types/chat'

interface ChatMessageProps {
	request: ClientChatRequest
}

const UserMessage = ({ request }: ChatMessageProps) => {
	return (
		<div className='flex justify-end'>
			<div
				className='
					max-w-[80%]
					rounded-2xl bg-muted
					px-5 py-3.5 text-base leading-relaxed
					break-words whitespace-pre-wrap font-sans shadow-md
				'
			>
				{request.userMessage.content.trim()}
			</div>
		</div>
	)
}

export default UserMessage
