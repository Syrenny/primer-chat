import { createStore } from 'zustand'
import { persist } from 'zustand/middleware'

interface LayoutState {
	panelSizes: number[]
	setPanelSizes: (sizes: number[]) => void
}

export const layoutStore = createStore(
	persist<LayoutState>(
		set => ({
			panelSizes: [30, 70],
			setPanelSizes: sizes => set({ panelSizes: sizes }),
		}),
		{
			name: 'layout-storage',
		}
	)
)
