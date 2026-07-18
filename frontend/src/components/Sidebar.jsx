import { NavLink } from 'react-router-dom'

const menuByRole = {
  employee: [
    { label: 'Tableau de bord', path: '/dashboard' },
    { label: 'Ressources', path: '/resources' },
    { label: 'Mes demandes', path: '/requests' },
  ],

  manager: [
    { label: 'Tableau de bord', path: '/dashboard' },
    {
      label: 'Demandes à valider',
      path: '/manager-requests',
    },
  ],

  it_admin: [
    { label: 'Tableau de bord', path: '/dashboard' },
    { label: 'Gestion des accès', path: '/grants' },
  ],

  security_admin: [
    { label: 'Tableau de bord', path: '/dashboard' },
    { label: 'Utilisateurs', path: '/users' },
    { label: 'Audit', path: '/audit' },
    { label: 'Monitoring', path: '/monitoring' },
  ],
}

function Sidebar({ role = 'employee' }) {
  const menuItems = menuByRole[role] || []

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <h2>AccessGuard</h2>
        <p>Gestion des accès</p>
      </div>

      <nav aria-label="Navigation principale">
        {menuItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              isActive
                ? 'sidebar-link active'
                : 'sidebar-link'
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}

export default Sidebar