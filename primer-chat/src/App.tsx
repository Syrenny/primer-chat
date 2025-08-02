import { Route, Routes } from 'react-router-dom'
import { ToastContainer } from 'react-toastify'
import './App.css'
import { ThemeProvider } from './components/ThemeProvider'
import Chat from './pages/Chat'

function App() {
	return (
		<ThemeProvider>
			<div className='h-dvh w-full'>
				<ToastContainer position='top-right' autoClose={2000} />
				<Routes>
					<Route path='/' element={<Chat />} />
					<Route path='/c/:historyId/' element={<Chat />} />
					<Route path='/c/:historyId/f/:fileId' element={<Chat />} />
					<Route path='/f/:fileId/' element={<Chat />} />
					<Route path='*' element={<Chat />} />
				</Routes>
			</div>
		</ThemeProvider>
	)
}

export default App
