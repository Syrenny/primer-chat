import { createStore } from 'zustand'
import { persist } from 'zustand/middleware'

interface UIState {
	isSidebarOpen: boolean
	isFilesModalOpen: boolean
	isAddFilesModalOpen: boolean
	openedChatIds: string[]
    addFilesModalChatId: string | null

	setOpenedChatIds: (ids: string[]) => void
	openSidebar: () => void
	closeSidebar: () => void
	toggleSidebar: () => void

	openFilesModal: () => void
	closeFilesModal: () => void
	toggleFilesModal: () => void


	openAddFilesModal: (historyId: string) => void
	closeAddFilesModal: () => void
}

export const uiStore = createStore(
	persist<UIState>(
		(set, _) => ({
			isSidebarOpen: true,
			isFilesModalOpen: false,
			isAddFilesModalOpen: false,
			openedChatIds: [],
			addFilesModalChatId: null,

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

			openAddFilesModal: historyId =>
				set({ addFilesModalChatId: historyId }),
			closeAddFilesModal: () => set({ addFilesModalChatId: null }),
		}),
		{
			name: 'ui-storage',
		}
	)
)
