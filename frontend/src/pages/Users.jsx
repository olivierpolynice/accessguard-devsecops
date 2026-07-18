import { useEffect, useRef, useState } from 'react'
import ErrorMessage from '../components/ErrorMessage'
import LoadingSpinner from '../components/LoadingSpinner'
import StatusBadge from '../components/StatusBadge'
import { apiRequest } from '../services/api'
import './Users.css'

const roleLabels = {
  employee: 'Employé',
  manager: 'Manager',
  it_admin: 'Administrateur IT',
  security_admin: 'Administrateur sécurité',
}

const availableRoles = [
  'employee',
  'manager',
  'it_admin',
  'security_admin',
]

const initialNewUser = {
  email: '',
  password: '',
  role: 'employee',
}

function formatDate(value) {
  if (!value) {
    return 'Non renseignée'
  }

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return 'Non renseignée'
  }

  return new Intl.DateTimeFormat('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  }).format(date)
}

function Users() {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const [showAddForm, setShowAddForm] = useState(false)
  const [newUser, setNewUser] = useState(initialNewUser)

  const [editingUserId, setEditingUserId] =
    useState(null)
  const [editingRole, setEditingRole] =
    useState('employee')

  const [processingType, setProcessingType] =
    useState('')
  const [processingId, setProcessingId] =
    useState(null)

  const [actionError, setActionError] = useState('')
  const [successMessage, setSuccessMessage] =
    useState('')

  const processingRef = useRef(false)

  useEffect(() => {
    let cancelled = false

    apiRequest('/users')
      .then((data) => {
        if (!cancelled) {
          setUsers(Array.isArray(data) ? data : [])
          setError('')
        }
      })
      .catch(() => {
        if (!cancelled) {
          setError(
            'Impossible de charger les utilisateurs.',
          )
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false)
        }
      })

    return () => {
      cancelled = true
    }
  }, [])

  async function handleReload() {
    setLoading(true)
    setError('')
    setActionError('')
    setSuccessMessage('')

    try {
      const data = await apiRequest('/users')
      setUsers(Array.isArray(data) ? data : [])
    } catch {
      setError(
        'Impossible de charger les utilisateurs.',
      )
    } finally {
      setLoading(false)
    }
  }

  async function handleAddUser(event) {
    event.preventDefault()

    if (processingRef.current) {
      return
    }

    processingRef.current = true
    setProcessingType('add')
    setProcessingId(null)
    setActionError('')
    setSuccessMessage('')

    try {
      const createdUser = await apiRequest('/users', {
        method: 'POST',
        body: JSON.stringify({
          email: newUser.email.trim(),
          password: newUser.password,
          role: newUser.role,
          is_active: true,
        }),
      })

      setUsers((currentUsers) => [
        createdUser,
        ...currentUsers,
      ])

      setNewUser(initialNewUser)
      setShowAddForm(false)
      setSuccessMessage(
        'L’utilisateur a bien été créé.',
      )
    } catch (creationError) {
      setActionError(
        creationError.message ||
          'Impossible de créer cet utilisateur.',
      )
    } finally {
      processingRef.current = false
      setProcessingType('')
      setProcessingId(null)
    }
  }

  function startRoleEdition(user) {
    if (processingRef.current) {
      return
    }

    setEditingUserId(user.id)
    setEditingRole(user.role)
    setActionError('')
    setSuccessMessage('')
  }

  function cancelRoleEdition() {
    setEditingUserId(null)
    setEditingRole('employee')
  }

  async function handleRoleUpdate(userId) {
    if (processingRef.current) {
      return
    }

    processingRef.current = true
    setProcessingType('role')
    setProcessingId(userId)
    setActionError('')
    setSuccessMessage('')

    try {
      const updatedUser = await apiRequest(
        `/users/${userId}/role`,
        {
          method: 'PATCH',
          body: JSON.stringify({
            role: editingRole,
          }),
        },
      )

      setUsers((currentUsers) =>
        currentUsers.map((user) =>
          user.id === userId
            ? {
                ...user,
                ...updatedUser,
                role: updatedUser?.role || editingRole,
              }
            : user,
        ),
      )

      setEditingUserId(null)
      setSuccessMessage(
        'Le rôle de l’utilisateur a été modifié.',
      )
    } catch (updateError) {
      setActionError(
        updateError.message ||
          'Impossible de modifier ce rôle.',
      )
    } finally {
      processingRef.current = false
      setProcessingType('')
      setProcessingId(null)
    }
  }

  async function handleStatusUpdate(user) {
    if (processingRef.current) {
      return
    }

    processingRef.current = true
    setProcessingType('status')
    setProcessingId(user.id)
    setActionError('')
    setSuccessMessage('')

    const nextStatus = !user.is_active

    try {
      const updatedUser = await apiRequest(
        `/users/${user.id}/status`,
        {
          method: 'PATCH',
          body: JSON.stringify({
            is_active: nextStatus,
          }),
        },
      )

      setUsers((currentUsers) =>
        currentUsers.map((currentUser) =>
          currentUser.id === user.id
            ? {
                ...currentUser,
                ...updatedUser,
                is_active:
                  updatedUser?.is_active ?? nextStatus,
              }
            : currentUser,
        ),
      )

      setSuccessMessage(
        nextStatus
          ? 'Le compte a été activé.'
          : 'Le compte a été désactivé.',
      )
    } catch (statusError) {
      setActionError(
        statusError.message ||
          'Impossible de modifier l’état du compte.',
      )
    } finally {
      processingRef.current = false
      setProcessingType('')
      setProcessingId(null)
    }
  }

  const operationInProgress = processingType !== ''

  return (
    <section className="page">
      <div className="users-header">
        <div>
          <h1>Gestion des utilisateurs</h1>

          <p>
            Administrez les comptes et les rôles AccessGuard.
          </p>
        </div>

        <div className="user-actions">
          <button
            className="edit-button"
            type="button"
            onClick={handleReload}
            disabled={loading || operationInProgress}
          >
            {loading ? 'Chargement...' : 'Actualiser'}
          </button>

          <button
            className="add-user-button"
            type="button"
            onClick={() => {
              setShowAddForm(
                (currentValue) => !currentValue,
              )
              setActionError('')
              setSuccessMessage('')
            }}
            disabled={loading || operationInProgress}
          >
            {processingType === 'add'
              ? 'Création...'
              : showAddForm
                ? 'Fermer le formulaire'
                : 'Ajouter un utilisateur'}
          </button>
        </div>
      </div>

      {successMessage && (
        <div className="success-message" role="status">
          {successMessage}
        </div>
      )}

      {actionError && (
        <ErrorMessage message={actionError} />
      )}

      {showAddForm && (
        <form
          className="user-form"
          onSubmit={handleAddUser}
        >
          <div className="form-group">
            <label htmlFor="new-user-email">
              Adresse e-mail
            </label>

            <input
              id="new-user-email"
              type="email"
              value={newUser.email}
              onChange={(event) =>
                setNewUser((currentUser) => ({
                  ...currentUser,
                  email: event.target.value,
                }))
              }
              placeholder="prenom.role@asteriatech.local"
              disabled={processingType === 'add'}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="new-user-password">
              Mot de passe
            </label>

            <input
              id="new-user-password"
              type="password"
              value={newUser.password}
              onChange={(event) =>
                setNewUser((currentUser) => ({
                  ...currentUser,
                  password: event.target.value,
                }))
              }
              placeholder="Mot de passe sécurisé"
              disabled={processingType === 'add'}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="new-user-role">Rôle</label>

            <select
              id="new-user-role"
              value={newUser.role}
              onChange={(event) =>
                setNewUser((currentUser) => ({
                  ...currentUser,
                  role: event.target.value,
                }))
              }
              disabled={processingType === 'add'}
            >
              {availableRoles.map((role) => (
                <option key={role} value={role}>
                  {roleLabels[role]}
                </option>
              ))}
            </select>
          </div>

          <button
            className="add-user-button"
            type="submit"
            disabled={
              processingType === 'add' ||
              !newUser.email.trim() ||
              !newUser.password
            }
          >
            {processingType === 'add'
              ? 'Création en cours...'
              : 'Créer l’utilisateur'}
          </button>
        </form>
      )}

      {loading && (
        <LoadingSpinner message="Chargement des utilisateurs..." />
      )}

      {error && (
        <ErrorMessage
          message={error}
          onRetry={handleReload}
        />
      )}

      {!loading && !error && users.length === 0 && (
        <p>Aucun utilisateur trouvé.</p>
      )}

      {!loading && !error && users.length > 0 && (
        <div className="table-container">
          <table className="users-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Adresse e-mail</th>
                <th>Rôle</th>
                <th>Statut</th>
                <th>Création</th>
                <th>Actions</th>
              </tr>
            </thead>

            <tbody>
              {users.map((user) => {
                const isEditing =
                  editingUserId === user.id

                const isProcessing =
                  processingId === user.id

                return (
                  <tr key={user.id}>
                    <td>{user.id}</td>
                    <td>{user.email}</td>

                    <td>
                      {isEditing ? (
                        <select
                          value={editingRole}
                          onChange={(event) =>
                            setEditingRole(
                              event.target.value,
                            )
                          }
                          disabled={isProcessing}
                        >
                          {availableRoles.map((role) => (
                            <option
                              key={role}
                              value={role}
                            >
                              {roleLabels[role]}
                            </option>
                          ))}
                        </select>
                      ) : (
                        roleLabels[user.role] || user.role
                      )}
                    </td>

                    <td>
                      <StatusBadge
                        status={
                          user.is_active
                            ? 'ACTIVE'
                            : 'INACTIVE'
                        }
                      />
                    </td>

                    <td>{formatDate(user.created_at)}</td>

                    <td>
                      <div className="user-actions">
                        {isEditing ? (
                          <>
                            <button
                              className="edit-button"
                              type="button"
                              onClick={() =>
                                handleRoleUpdate(user.id)
                              }
                              disabled={operationInProgress}
                            >
                              {isProcessing &&
                              processingType === 'role'
                                ? 'Traitement...'
                                : 'Enregistrer'}
                            </button>

                            <button
                              className="disable-button"
                              type="button"
                              onClick={cancelRoleEdition}
                              disabled={operationInProgress}
                            >
                              Annuler
                            </button>
                          </>
                        ) : (
                          <button
                            className="edit-button"
                            type="button"
                            onClick={() =>
                              startRoleEdition(user)
                            }
                            disabled={operationInProgress}
                          >
                            Modifier
                          </button>
                        )}

                        <button
                          className="disable-button"
                          type="button"
                          onClick={() =>
                            handleStatusUpdate(user)
                          }
                          disabled={operationInProgress}
                        >
                          {isProcessing &&
                          processingType === 'status'
                            ? 'Traitement...'
                            : user.is_active
                              ? 'Désactiver'
                              : 'Activer'}
                        </button>
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}

export default Users