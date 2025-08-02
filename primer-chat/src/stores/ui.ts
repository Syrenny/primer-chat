import { createStore } from 'zustand'

interface UIState {
	isSidebarOpen: boolean
	isFilesModalOpen: boolean
	isAddFilesModalOpen: boolean

	openSidebar: () => void
	closeSidebar: () => void
	toggleSidebar: () => void

	openFilesModal: () => void
	closeFilesModal: () => void
	toggleFilesModal: () => void

	openAddFilesModal: () => void
	closeAddFilesModal: () => void
}

export const uiStore = createStore<UIState>(set => ({
	isSidebarOpen: true,
	isFilesModalOpen: false,
	isAddFilesModalOpen: false,

	openSidebar: () => set({ isSidebarOpen: true }),
	closeSidebar: () => set({ isSidebarOpen: false }),
	toggleSidebar: () => set(s => ({ isSidebarOpen: !s.isSidebarOpen })),

	openFilesModal: () => set({ isFilesModalOpen: true }),
	closeFilesModal: () => set({ isFilesModalOpen: false }),
	toggleFilesModal: () =>
		set(s => ({ isFilesModalOpen: !s.isFilesModalOpen })),

	openAddFilesModal: () => set({ isAddFilesModalOpen: true }),
	closeAddFilesModal: () => set({ isAddFilesModalOpen: false }),
}))
