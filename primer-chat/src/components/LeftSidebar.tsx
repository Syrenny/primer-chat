import { Separator } from '@/components/ui/separator'
import { uiStore } from '@/stores/ui'
import { useStore } from 'zustand'
import ChatSection from './ChatSection'
import FileSection from './FileSection'

export default function LeftSidebar() {
	const isSidebarOpen = useStore(uiStore, s => s.isSidebarOpen)

	return (
		<aside
			className={`
				h-full flex flex-col
				bg-sidebar border-r border-border shadow-lg
				transition-all duration-300 ease-in-out
				${isSidebarOpen ? 'w-80' : 'w-0 overflow-hidden'}
			`}
		>
			<FileSection />
			<Separator />
			<ChatSection />
		</aside>
	)
}
