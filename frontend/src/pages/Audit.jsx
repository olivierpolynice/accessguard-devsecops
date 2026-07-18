import { useEffect, useState } from 'react'
import ErrorMessage from '../components/ErrorMessage'
import LoadingSpinner from '../components/LoadingSpinner'
import { apiRequest } from '../services/api'
import './Audit.css'

function formatDateTime(value) {
  if (!value) {
    return 'Non renseignée'
  }

  return new Intl.DateTimeFormat('fr-FR', {
    dateStyle: 'short',
    timeStyle: 'short',
  }).format(new Date(value))
}

function getResultClass(result) {
  const normalizedResult = String(result).toUpperCase()

  if (
    normalizedResult === 'SUCCESS' ||
    normalizedResult === 'SUCCÈS'
  ) {
    return 'audit-result-success'
  }

  if (
    normalizedResult === 'DENIED' ||
    normalizedResult === 'REFUSÉ' ||
    normalizedResult === 'FORBIDDEN'
  ) {
    return 'audit-result-denied'
  }

  return 'audit-result-failure'
}

function getResultLabel(result) {
  const labels = {
    SUCCESS: 'Succès',
    DENIED: 'Refusé',
    FORBIDDEN: 'Refusé',
    FAILURE: 'Échec',
    FAILED: 'Échec',
    ERROR: 'Échec',
  }

  const normalizedResult = String(
    result || 'SUCCESS',
  ).toUpperCase()

  return labels[normalizedResult] || result || 'Succès'
}

function Audit() {
  const [auditLogs, setAuditLogs] = useState([])
  const [resources, setResources] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false

    Promise.all([
      apiRequest('/audit-logs'),
      apiRequest('/resources'),
    ])
      .then(([logsData, resourcesData]) => {
        if (!cancelled) {
          setAuditLogs(
            Array.isArray(logsData) ? logsData : [],
          )

          setResources(
            Array.isArray(resourcesData)
              ? resourcesData
              : [],
          )

          setError('')
        }
      })
      .catch(() => {
        if (!cancelled) {
          setError(
            'Impossible de charger le journal d’audit.',
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
      const [logsData, resourcesData] =
        await Promise.all([
          apiRequest('/audit-logs'),
          apiRequest('/resources'),
        ])

      setAuditLogs(
        Array.isArray(logsData) ? logsData : [],
      )

      setResources(
        Array.isArray(resourcesData) ? resourcesData : [],
      )
    } catch {
      setError(
        'Impossible de charger le journal d’audit.',
      )
    } finally {
      setLoading(false)
    }
  }

  function getResourceName(resourceId) {
    if (!resourceId) {
      return 'AccessGuard'
    }

    const resource = resources.find(
      (item) => item.id === resourceId,
    )

    return resource?.name || `Ressource ${resourceId}`
  }

  function handleExport() {
    console.log('Export du journal d’audit')
  }

  return (
    <section className="page">
      <div className="audit-header">
        <div>
          <h1>Journal d’audit</h1>
          <p>
            Consultez les événements de sécurité enregistrés.
          </p>
        </div>

        <div className="user-actions">
          <button
            className="export-audit-button"
            type="button"
            onClick={handleReload}
            disabled={loading}
          >
            Actualiser
          </button>

          <button
            className="export-audit-button"
            type="button"
            onClick={handleExport}
          >
            Exporter le journal
          </button>
        </div>
      </div>

      {loading && (
        <LoadingSpinner message="Chargement du journal d’audit..." />
      )}

      {error && (
        <ErrorMessage
          message={error}
          onRetry={handleReload}
        />
      )}

      {!loading && !error && auditLogs.length === 0 && (
        <p>Aucun événement d’audit enregistré.</p>
      )}

      {!loading && !error && auditLogs.length > 0 && (
        <div className="table-container">
          <table className="audit-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Date et heure</th>
                <th>Utilisateur</th>
                <th>Action</th>
                <th>Ressource</th>
                <th>Résultat</th>
              </tr>
            </thead>

            <tbody>
              {auditLogs.map((log) => {
                const result =
                  log.result ||
                  log.outcome ||
                  log.status ||
                  'SUCCESS'

                return (
                  <tr key={log.id}>
                    <td>{log.id}</td>

                    <td>
                      {formatDateTime(
                        log.created_at ||
                          log.timestamp ||
                          log.date,
                      )}
                    </td>

                    <td>
                      {log.user_email ||
                        log.actor_email ||
                        log.user ||
                        'Utilisateur inconnu'}
                    </td>

                    <td>
                      {log.action ||
                        log.event_type ||
                        'Événement'}
                    </td>

                    <td>
                      {log.resource_name ||
                        getResourceName(
                          log.resource_id,
                        )}
                    </td>

                    <td>
                      <span
                        className={`audit-result ${getResultClass(
                          result,
                        )}`}
                      >
                        {getResultLabel(result)}
                      </span>
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

export default Audit