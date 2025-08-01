import {
	apiFileDelete,
	apiFileLink,
	apiFileList,
	apiFileStatus,
	apiFileUpload,
} from '@/api/files'
import type { ApiFileLinkResponse, ApiFileResponse } from '@/types/files'
import { createStore } from 'zustand'

interface FileStoreState {
	files: ApiFileResponse[]
	loading: boolean
	error: string | null

	fetchFiles: () => Promise<void>
	uploadFile: (file: File) => Promise<void>
	deleteFile: (fileId: string) => Promise<void>
	refreshStatus: (fileId: string) => Promise<void>
	getFileLink: (fileId: string) => Promise<ApiFileLinkResponse | null>
}

export const fileStore = createStore<FileStoreState>((set, get) => ({
	files: [],
	loading: false,
	error: null,

	fetchFiles: async () => {
		set({ loading: true, error: null })
		try {
			const files = await apiFileList()
			set({ files })
		} catch (error) {
			console.error(error)
			set({ error: 'Не удалось загрузить список файлов' })
		} finally {
			set({ loading: false })
		}
	},

	uploadFile: async (file: File) => {
        const existing = get().files.find(f => f.filename === file.name)
		if (existing) {
			set({ error: `Файл с именем "${file.name}" уже загружен` })
			return
		}

		set({ loading: true, error: null })
		try {
			await apiFileUpload(file)
			await get().fetchFiles()
		} catch (error) {
			console.error(error)
			set({ error: 'Ошибка загрузки файла' })
		} finally {
			set({ loading: false })
		}
	},

	deleteFile: async (fileId: string) => {
		set({ loading: true, error: null })
		try {
			await apiFileDelete(fileId)
			const updatedFiles = get().files.filter(f => f.file_id !== fileId)
			set({ files: updatedFiles })
		} catch (error) {
			console.error(error)
			set({ error: 'Ошибка удаления файла' })
		} finally {
			set({ loading: false })
		}
	},

	refreshStatus: async (fileId: string) => {
		try {
			const status = await apiFileStatus(fileId)
			const updatedFiles = get().files.map(f =>
				f.file_id === fileId
					? { ...f, is_indexed: status.is_indexed }
					: f
			)
			set({ files: updatedFiles })
		} catch (error) {
			console.error(error)
			set({ error: 'Ошибка получения статуса файла' })
		}
	},

	getFileLink: async (fileId: string) => {
		try {
			return await apiFileLink(fileId)
		} catch (error) {
			console.error(error)
			set({ error: 'Ошибка получения ссылки на файл' })
			return null
		}
	},
}))
