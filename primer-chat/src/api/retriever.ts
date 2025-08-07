import type { IndexedChunk } from '@/types/chunks'
import apiClient from './base'

export const apiRetrieverRetrieve = async (
	historyId: string,
	query: string
): Promise<IndexedChunk[]> => {
	const request = {
		history_id: historyId,
		query: query,
	}
	const { data } = await apiClient.post('/api/retrieve', request)
	return data.chunks
}
