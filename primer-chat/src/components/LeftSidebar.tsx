import { Separator } from '@/components/ui/separator'
import { uiStore } from '@/stores/ui'
import { ScrollArea, ScrollBar } from '@/components/ui/scroll-area'
import { useStore } from 'zustand'
import ChatSection from './ChatSection'

export default function LeftSidebar() {
	const isSidebarOpen = useStore(uiStore, s => s.isSidebarOpen)

	return (
		<aside
			className={`
				h-dvh flex flex-col
				bg-sidebar border-r border-border shadow-lg
				transition-all duration-300 ease-in-out z-10
				${isSidebarOpen ? 'w-80' : 'w-0 overflow-hidden'}
			`}
		>
			<ScrollArea className='overflow-y-auto w-full h-full '>
				<Separator />
				<ChatSection />
				<ScrollBar orientation='vertical' />
			</ScrollArea>
		</aside>
	)
}
