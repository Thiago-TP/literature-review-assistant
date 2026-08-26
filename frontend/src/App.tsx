import { Route, Routes } from 'react-router-dom'
import ProjectListPage from './pages/ProjectListPage'
import ReviewWorkspacePage from './pages/ReviewWorkspacePage'
import DashboardPage from './pages/DashboardPage'

function App() {
  return (
    <Routes>
      <Route path="/" element={<ProjectListPage />} />
      <Route path="/projects/:projectId" element={<ReviewWorkspacePage />} />
      <Route path="/projects/:projectId/dashboard" element={<DashboardPage />} />
    </Routes>
  )
}

export default App
