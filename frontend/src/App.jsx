import { Route, Routes } from 'react-router-dom'

import MainLayout from './components/MainLayout'

import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Resources from './pages/Resources'
import Requests from './pages/Requests'
import ManagerRequests from './pages/ManagerRequests'
import Grants from './pages/Grants'
import Audit from './pages/Audit'
import Users from './pages/Users'
import Monitoring from './pages/Monitoring'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Login />} />

      <Route element={<MainLayout />}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/resources" element={<Resources />} />
        <Route path="/requests" element={<Requests />} />

        <Route
          path="/manager-requests"
          element={<ManagerRequests />}
        />

        <Route path="/grants" element={<Grants />} />
        <Route path="/audit" element={<Audit />} />
        <Route path="/users" element={<Users />} />
        <Route path="/monitoring" element={<Monitoring />} />
      </Route>
    </Routes>
  )
}

export default App