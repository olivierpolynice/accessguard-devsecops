function Header({ user, onLogout }) {
  return (
    <header className="header">
      <div>
        <p>Utilisateur connecté</p>
        <strong>{user?.email || 'Utilisateur AccessGuard'}</strong>
        <span>{user?.role || 'Rôle non défini'}</span>
      </div>

      <button type="button" onClick={onLogout}>
        Se déconnecter
      </button>
    </header>
  )
}

export default Header