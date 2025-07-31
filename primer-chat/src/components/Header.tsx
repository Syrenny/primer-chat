import { cn } from '@/lib/utils'

const Header = () => {
	return (
		<header
			className={cn(
				'bg-background/80 border-b border-border shadow-sm sticky top-0 z-50 backdrop-blur'
			)}
		>
			<div className='max-w-3xl w-full mx-auto px-4 py-3 flex items-center justify-between'>
				<div className='flex flex-col items-start'>
					<span className='text-xl font-semibold text-foreground tracking-tight'>
						Primer Chat
					</span>
					<span className='text-xs text-muted-foreground tracking-wide'>
						AI Talent Hub JMLC
					</span>
				</div>
			</div>
		</header>
	)
}

export default Header
