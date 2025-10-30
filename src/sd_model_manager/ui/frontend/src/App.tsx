import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Sidebar from './components/layout/Sidebar'
import MainLayout from './components/layout/MainLayout'
import DownloadPage from './pages/DownloadPage'

function App() {
  return (
    <Router>
      <div className="flex h-screen bg-gray-100">
        <Sidebar />
        <MainLayout>
          <Routes>
            <Route path="/download" element={<DownloadPage />} />
            <Route path="/" element={<DownloadPage />} />
          </Routes>
        </MainLayout>
      </div>
    </Router>
  )
}

export default App
