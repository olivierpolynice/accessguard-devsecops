import { useEffect, useState } from 'react'
import ErrorMessage from '../components/ErrorMessage'
import LoadingSpinner from '../components/LoadingSpinner'
import { apiRequest } from '../services/api'
import './Resources.css'

const sensitivityLabels = {
  LOW: 'Faible',
  MEDIUM: 'Moyenne',
  HIGH: 'Élevée',
  CRITICAL: 'Critique',
}

function Resources() {
  const [resources, setResources] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false

    apiRequest('/resources')
      .then((data) => {
        if (!cancelled) {
          setResources(Array.isArray(data) ? data : [])
          setError('')
        }
      })
      .catch(() => {
        if (!cancelled) {
          setError(
            'Impossible de charger les ressources.',
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

    try {
      const data = await apiRequest('/resources')
      setResources(Array.isArray(data) ? data : [])
    } catch {
      setError('Impossible de charger les ressources.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="page">
      <div className="resources-header">
        <div>
          <h1>Ressources</h1>

          <p>
            Consultez les ressources disponibles dans
            AccessGuard.
          </p>
        </div>

        <button
          className="request-access-button"
          type="button"
          onClick={handleReload}
          disabled={loading}
        >
          {loading ? 'Chargement...' : 'Actualiser'}
        </button>
      </div>

      {loading && (
        <LoadingSpinner message="Chargement des ressources..." />
      )}

      {error && (
        <ErrorMessage
          message={error}
          onRetry={handleReload}
        />
      )}

      {!loading && !error && resources.length === 0 && (
        <p>Aucune ressource disponible.</p>
      )}

      {!loading && !error && resources.length > 0 && (
        <div className="table-container">
          <table className="resources-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Nom</th>
                <th>Description</th>
                <th>Sensibilité</th>
                <th>Statut</th>
                <th>Action</th>
              </tr>
            </thead>

            <tbody>
              {resources.map((resource) => (
                <tr key={resource.id}>
                  <td>{resource.id}</td>

                  <td>{resource.name}</td>

                  <td>
                    {resource.description ||
                      'Aucune description'}
                  </td>

                  <td>
                    <span
                      className={`sensitivity sensitivity-${String(
                        resource.sensitivity,
                      ).toLowerCase()}`}
                    >
                      {sensitivityLabels[
                        resource.sensitivity
                      ] || resource.sensitivity}
                    </span>
                  </td>

                  <td>
                    {resource.is_active
                      ? 'Disponible'
                      : 'Indisponible'}
                  </td>

                  <td>
                    <button
                      className="request-access-button"
                      type="button"
                      disabled={
                        loading || !resource.is_active
                      }
                    >
                      {loading
                        ? 'Traitement...'
                        : 'Demander l’accès'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}

export default Resources