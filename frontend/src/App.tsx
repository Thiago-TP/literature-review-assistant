import { Route, Routes } from 'react-router-dom'
import ProjectListPage from './pages/ProjectListPage'
import ReviewWorkspacePage from './pages/ReviewWorkspacePage'

function App() {
  return (
    <Routes>
      <Route path="/" element={<ProjectListPage />} />
      <Route path="/projects/:projectId" element={<ReviewWorkspacePage />} />
    </Routes>
  )
}

export default App
