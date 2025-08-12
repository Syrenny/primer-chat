import {
	apiFileDelete,
	apiFileLink,
	apiFileList,
	apiFileStatus,
	apiFileUpload,
} from '@/api/files'
import {
	type ApiFileLinkResponse,
	type ApiFileResponse,
	type ApiFileUploadProgress,
	ProgressStatus,
} from '@/types/files'
import { createStore } from 'zustand'

interface FileStoreState {
	files: ApiFileResponse[]
	uploadProgress: Record<string, number>
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
	uploadProgress: {},
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
		// запрет по имени
		const existsByName = get().files.some(f => f.filename === file.name)
		if (existsByName) {
			set({ error: `Файл с именем "${file.name}" уже загружен` })
			return
		}

		set({ error: null })
		let currentFileId: string | null = null

		try {
			await apiFileUpload(
				file,
				// onData (унифицировано: progress 0..1)
				(evt: ApiFileUploadProgress) => {
					if (evt.type === ProgressStatus.Response) {
						const { file_id, filename, progress } = evt
						currentFileId = file_id

						// если файла ещё нет — добавляем оптимистично
						const files = get().files
						if (!files.some(f => f.file_id === file_id)) {
							set({
								files: [
									...files,
									{
										file_id,
										filename,
										is_indexed: false,
									} as ApiFileResponse,
								],
							})
						}

						// обновляем прогресс 0..1
						set(state => ({
							uploadProgress: {
								...state.uploadProgress,
								[file_id]: progress,
							},
						}))

						// если прогресс завершён — считаем индексацию законченной
						if (progress >= 1) {
							set(state => ({
								files: state.files.map(f =>
									f.file_id === file_id
										? { ...f, is_indexed: true }
										: f
								),
							}))
							// убираем прогресс
							set(state => {
								const next = { ...state.uploadProgress }
								delete next[file_id]
								return { uploadProgress: next }
							})
						}
					} else {
						// ProgressStatus.Error
						set({ error: `Ошибка загрузки файла "${file.name}"` })
						if (currentFileId) {
							set(state => {
								const next = { ...state.uploadProgress }
								delete next[currentFileId as string]
								return { uploadProgress: next }
							})
						}
					}
				},
				// onDone
				() => {
				},
				// onError
				(err: unknown) => {
					console.error(err)
					set({ error: `Ошибка загрузки файла "${file.name}"` })
					if (currentFileId) {
						set(state => {
							const next = { ...state.uploadProgress }
							delete next[currentFileId as string]
							return { uploadProgress: next }
						})
					}
				}
			)
		} catch (error) {
			console.error(error)
			set({ error: `Ошибка загрузки файла "${file.name}"` })
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
