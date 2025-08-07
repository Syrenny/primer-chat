export type PdfLinePosition = {
	page: number
	xyxy: [number, number, number, number]
}

export type HTMLTag = 'h1' | 'h2' | 'h3' | 'p'

export type IndexedChunk = {
	content: string
	embedding: number[]
	html_tag: HTMLTag
	position: PdfLinePosition[]
}
