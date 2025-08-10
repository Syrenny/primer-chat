import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from '@/components/ui/card'
import { Info } from 'lucide-react'

export const ChatIntroduction = () => {
	return (
		<div className='h-full w-full'>
			<div className='absolute inset-0'>
				<div className='absolute top-0 -z-10 h-full w-full bg-background [&>div]:absolute [&>div]:bottom-auto [&>div]:left-auto [&>div]:right-0 [&>div]:top-0 [&>div]:h-[500px] [&>div]:w-[200px] [&>div]:-translate-x-[30px] [&>div]:translate-y-[150px] [&>div]:rounded-full [&>div]:bg-primary [&>div]:opacity-50 [&>div]:blur-[160px]'>
					<div></div>
				</div>
			</div>
			<div className='w-full h-full flex justify-start items-center flex-col mt-28'>
				<Card className='w-full max-w-xl shadow-md border-muted bg-muted/30'>
					<CardHeader>
						<CardTitle className='text-2xl'>
							Добро пожаловать!
						</CardTitle>
						<CardDescription className='text-sm text-muted-foreground'>
							Выберите или создайте чат, чтобы начать диалог по
							вашим документам.
						</CardDescription>
					</CardHeader>

					<CardContent className='space-y-4'>
						<Alert>
							<Info className='h-4 w-4' />
							<AlertTitle>Что можно делать:</AlertTitle>
							<AlertDescription>
								<ul className='list-disc list-inside space-y-1 text-sm text-muted-foreground'>
									<li>
										Загрузите PDF-документ через меню "Мои
										файлы"
									</li>
									<li>Создайте чат и добавьте файл</li>
									<li>
										Задавайте вопросы по содержанию
										документа
									</li>
								</ul>
							</AlertDescription>
						</Alert>
					</CardContent>
				</Card>
			</div>
		</div>
	)
}
