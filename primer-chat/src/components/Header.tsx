const Header = () => {
	return (
		<header className='h-16 shrink-0 w-full bg-background border-b shadow-sm backdrop-blur'>
			<div className='h-full w-full flex items-center justify-center'>
				<div className='flex flex-col'>
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
