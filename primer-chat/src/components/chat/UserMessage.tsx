import { type ClientChatMessage } from '../../types/chat'

interface ChatMessageProps {
	message: ClientChatMessage
}

const UserMessage = ({ message }: ChatMessageProps) => {
	return (
		<div className='relative'>
			<div
				className='mr-1 ml-auto max-w-[80%] w-fit rounded-2xl bg-[#e5e5ea] dark:bg-[#2f2f2f]
	px-5 py-3.5 text-[16px] leading-relaxed text-gray-800 dark:text-gray-200
	break-words whitespace-pre-wrap font-sans shadow-sm'
				data-message-type='user'
				role='presentation'
			>
				{message.data.content.trim()}
			</div>
			<div
				className='absolute top-0 -right-3 w-0 h-0 -z-10
	border-t-[0px] border-t-transparent
	border-b-[30px] border-b-transparent
	border-l-[30px] border-l-[#e5e5ea] dark:border-l-[#2f2f2f]'
			></div>
		</div>
	)
}

export default UserMessage
