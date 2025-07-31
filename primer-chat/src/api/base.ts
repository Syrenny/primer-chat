import axios from 'axios'

const apiClient = axios.create({
	baseURL: ``,
	headers: {
		'Content-Type': 'application/json',
	},
	withCredentials: true,
})

apiClient.interceptors.response.use(
	response => response,
	error => {
		console.error(error)

		return Promise.reject(error)
	}
)

export default apiClient
