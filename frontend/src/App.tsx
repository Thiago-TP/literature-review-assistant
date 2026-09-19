import { Route, Routes } from 'react-router-dom'
import ProjectListPage from './pages/ProjectListPage'
import ReviewWorkspacePage from './pages/ReviewWorkspacePage'
import DashboardPage from './pages/DashboardPage'
import HelpPage from './pages/HelpPage'
import ReviewPlanPage from './pages/ReviewPlanPage'
import { useSessionHeartbeat } from './hooks/useSessionHeartbeat'

function App() {
  useSessionHeartbeat()

  return (
    <Routes>
      <Route path="/" element={<ProjectListPage />} />
      <Route path="/projects/:projectId" element={<ReviewWorkspacePage />} />
      <Route path="/projects/:projectId/dashboard" element={<DashboardPage />} />
      <Route path="/projects/:projectId/plan" element={<ReviewPlanPage />} />
      <Route path="/help" element={<HelpPage />} />
    </Routes>
  )
}

export default App
