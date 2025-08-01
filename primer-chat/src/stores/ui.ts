import { createStore } from 'zustand'

interface UIState {
	isSidebarOpen: boolean

	openSidebar: () => void
	closeSidebar: () => void
	toggleSidebar: () => void
}

export const uiStore = createStore<UIState>(set => ({
	isSidebarOpen: true,

	openSidebar: () => set({ isSidebarOpen: true }),
	closeSidebar: () => set({ isSidebarOpen: false }),
	toggleSidebar: () => set(s => ({ isSidebarOpen: !s.isSidebarOpen })),
}))
