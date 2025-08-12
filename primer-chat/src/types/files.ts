export interface ApiFileResponse {
	file_id: string
	filename: string
	is_indexed: boolean
}

export interface ApiFileStatusResponse {
	file_id: string
	is_indexed: boolean
}

export interface ApiFileLinkResponse {
	url: string
}

export const ProgressStatus = {
	Response: 'response',
	Error: 'error',
} as const

export type ApiFileUploadProgress =
	| {
			type: typeof ProgressStatus.Response
			file_id: string
			filename: string
			progress: number
	  }
	| { type: typeof ProgressStatus.Error }
