import { type ClientChatMessage } from '../../types/chat'
import MarkdownRenderer from './markdown/MarkdownRenderer'
import { RetrievedChunks } from './RetrievedChunks'

interface ChatMessageProps {
	message: ClientChatMessage
}

const sampleChunks = [
	{
		id: 'chunk-1',
		page: 3,
		documentName: 'attention-is-all-you-need.pdf',
		preview:
			'…глубинное обучение использует многослойные нейронные сети для извлечения признаков…',
		onClick: () => console.log('Перейти к chunk-1'),
	},
	{
		id: 'chunk-2',
		page: 5,
		documentName: 'attention-is-all-you-need.pdf',
		preview:
			'…функция активации определяет выход нейрона в зависимости от входных данных…',
		onClick: () => console.log('Перейти к chunk-2'),
	},
	{
		id: 'chunk-3',
		page: 6,
		documentName: 'attention-is-all-you-need.pdf',
		preview: '…градиент показывает направление наибольшего роста функции…',
		onClick: () => console.log('Перейти к chunk-3'),
	},
]

const AssistantMessage = ({ message }: ChatMessageProps) => {
	return (
		<div className='w-full flex flex-col h-full'>
			<MarkdownRenderer content={message.data.content} />
			<RetrievedChunks chunks={sampleChunks} />
		</div>
	)
}

export default AssistantMessage
