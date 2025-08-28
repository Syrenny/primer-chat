import { Button } from '@/components/ui/button'
import { uiStore } from '@/stores/ui'
import { Menu } from 'lucide-react'
import { useStore } from 'zustand'
import { ThemeToggle } from './ThemeToggle'

const Header = () => {
	const toggleSidebar = useStore(uiStore, s => s.toggleSidebar)

	return (
		<header className='flex flex-row justify-between items-center h-10 w-full border-b border-border bg-popover select-none pr-4 pl-4'>
			<div className='flex items-center justify-between'>
				<Button variant='ghost' size='icon' onClick={toggleSidebar}>
					<Menu className='w-5 h-5' />
				</Button>
				<div className='flex flex-row flex-1 ml-6 truncate items-end gap-4'>
					<span className='text-xl font-semibold text-foreground truncate'>
						Primer Chat
					</span>
				</div>
			</div>
			<ThemeToggle />
		</header>
	)
}

export default Header
