import { createStore } from 'zustand'
import { persist } from 'zustand/middleware'

interface UIState {
	isSidebarOpen: boolean
	isFilesModalOpen: boolean
	isAddFilesModalOpen: boolean
	openedChatIds: string[]

	setOpenedChatIds: (ids: string[]) => void
	openSidebar: () => void
	closeSidebar: () => void
	toggleSidebar: () => void

	openFilesModal: () => void
	closeFilesModal: () => void
	toggleFilesModal: () => void

	openAddFilesModal: () => void
	closeAddFilesModal: () => void
}

export const uiStore = createStore(
	persist<UIState>(
		(set, get) => ({
			isSidebarOpen: true,
			isFilesModalOpen: false,
			isAddFilesModalOpen: false,
			openedChatIds: [],

			setOpenedChatIds: ids => set({ openedChatIds: ids }),

			openSidebar: () => set({ isSidebarOpen: true }),
			closeSidebar: () => set({ isSidebarOpen: false }),
			toggleSidebar: () =>
				set(state => ({ isSidebarOpen: !state.isSidebarOpen })),

			openFilesModal: () => set({ isFilesModalOpen: true }),
			closeFilesModal: () => set({ isFilesModalOpen: false }),
			toggleFilesModal: () =>
				set(state => ({
					isFilesModalOpen: !state.isFilesModalOpen,
				})),

			openAddFilesModal: () => set({ isAddFilesModalOpen: true }),
			closeAddFilesModal: () => set({ isAddFilesModalOpen: false }),
		}),
		{
			name: 'ui-storage',
		}
	)
)
