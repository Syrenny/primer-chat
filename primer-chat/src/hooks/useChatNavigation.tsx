import { generatePath, useNavigate, useParams } from 'react-router-dom'

export function useChatNavigation() {
	const navigate = useNavigate()
	const { historyId, fileId } = useParams()

	return {
		historyId,
		fileId,
		goTo: (newHistoryId: string, newFileId: string) => {
			const path = generatePath('/c/:historyId/f/:fileId', {
				historyId: newHistoryId,
				fileId: newFileId,
			})
			navigate(path)
		},
		goToChat: (newHistoryId: string) => {
			const path = generatePath('/c/:historyId', {
				historyId: newHistoryId,
			})
			navigate(path)
		},
	}
}
