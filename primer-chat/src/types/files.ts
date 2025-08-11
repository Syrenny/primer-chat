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
