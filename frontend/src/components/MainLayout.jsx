import {
  Outlet,
  useNavigate,
} from 'react-router-dom'
import Sidebar from './Sidebar'
import Header from './Header'

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

function MainLayout() {
  const navigate = useNavigate()

  const token =
    localStorage.getItem('access_token')

  const tokenPayload = token
    ? decodeToken(token)
    : null

  const user = {
    email:
      tokenPayload?.email ||
      tokenPayload?.sub ||
      'Utilisateur AccessGuard',

    role:
      tokenPayload?.role ||
      'employee',
  }

  function handleLogout() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('token_type')

    navigate('/', {
      replace: true,
    })
  }

  return (
    <div className="app-layout">
      <Sidebar role={user.role} />

      <div className="app-content">
        <Header
          user={user}
          onLogout={handleLogout}
        />

        <main className="main-content">
          <Outlet context={{ user }} />
        </main>
      </div>
    </div>
  )
}

export default MainLayout