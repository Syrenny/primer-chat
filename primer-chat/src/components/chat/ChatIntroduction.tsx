import { useMemo } from 'react'


const tipsPool = [
	{
		title: 'Аллергии и предпочтения',
		description:
			'Сообщите мне о своих ограничениях — подберу подходящие блюда',
	},
]

export const ChatIntroduction = () => {

	return (
		<div className='w-full mx-auto flex flex-col gap-3 px-2 pt-2'>
			<div className='w-full grid gap-2 justify-center'>

				<div className='w-full flex items-center gap-2 justify-between px-4 py-2 rounded-md'></div>

				<div className='flex flex-col w-full'>
					{tipsPool.map(({ title, description }, idx) => (
						<button
							key={idx}
							aria-label='Открыть настройки предпочтений'
							className='flex flex-col mb-2 rounded-lg  p-3 shadow-sm hover:shadow-md transition-shadow text-left'
						>
							<strong className='text-[16px] text-gray-700 dark:text-gray-200'>
								{title}
							</strong>
							<span className='text-[14px] text-gray-600 dark:text-gray-300'>
								{description}
							</span>
						</button>
					))}
				</div>
			</div>
		</div>
	)
}
