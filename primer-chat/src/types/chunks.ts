export type PdfLinePosition = {
	page: number
	xyxy: [number, number, number, number]
}

export type IndexedChunk = {
	file_id: string
	filename: string
	positions: PdfLinePosition[]
}
