import { Navigate, Outlet } from 'react-router-dom'

function decodeToken(token) {
  try {
    const payload = token.split('.')[1]

    const normalizedPayload = payload
      .replaceAll('-', '+')
      .replaceAll('_', '/')

    return JSON.parse(atob(normalizedPayload))
  } catch {
    return null
  }
}

function ProtectedRoute({ allowedRoles }) {
  const token = localStorage.getItem('access_token')
  const tokenPayload = token ? decodeToken(token) : null

  if (!token || !tokenPayload) {
    return <Navigate to="/" replace />
  }

  if (
    allowedRoles &&
    !allowedRoles.includes(tokenPayload.role)
  ) {
    return <Navigate to="/dashboard" replace />
  }

  return <Outlet />
}

export default ProtectedRoute