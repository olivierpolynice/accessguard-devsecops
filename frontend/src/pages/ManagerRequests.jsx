import {
  useCallback,
  useEffect,
  useState,
} from 'react'
import ErrorMessage from '../components/ErrorMessage'
import LoadingSpinner from '../components/LoadingSpinner'
import StatusBadge from '../components/StatusBadge'
import { apiRequest } from '../services/api'
import './ManagerRequests.css'

function formatDate(value) {
  if (!value) {
    return 'Non renseignée'
  }

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return value
  }

  return new Intl.DateTimeFormat('fr-FR').format(date)
}

function ManagerRequests() {
  const [requests, setRequests] = useState([])
  const [resources, setResources] = useState([])
  const [comments, setComments] = useState({})
  const [loading, setLoading] = useState(true)
  const [actionLoadingId, setActionLoadingId] =
    useState(null)
  const [loadError, setLoadError] = useState('')
  const [actionError, setActionError] = useState('')
  const [successMessage, setSuccessMessage] =
    useState('')

  const loadRequests = useCallback(async () => {
    setLoading(true)
    setLoadError('')
    setActionError('')
    setSuccessMessage('')

    try {
      const [requestsData, resourcesData] =
        await Promise.all([
          apiRequest('/access-requests'),
          apiRequest('/resources'),
        ])

      setRequests(
        Array.isArray(requestsData)
          ? requestsData
          : [],
      )

      setResources(
        Array.isArray(resourcesData)
          ? resourcesData
          : [],
      )
    } catch (error) {
      setRequests([])
      setResources([])

      setLoadError(
        error.message ||
          'Impossible de charger les demandes à valider.',
      )
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      loadRequests()
    }, 0)

    return () => {
      window.clearTimeout(timeoutId)
    }
  }, [loadRequests])

  function getResourceName(resourceId) {
    const resource = resources.find(
      (item) =>
        Number(item.id) === Number(resourceId),
    )

    return (
      resource?.name ||
      `Ressource n°${resourceId}`
    )
  }

  function handleCommentChange(requestId, value) {
    setComments((currentComments) => ({
      ...currentComments,
      [requestId]: value,
    }))

    setActionError('')
    setSuccessMessage('')
  }

  async function handleDecision(
    requestId,
    decision,
  ) {
    const comment =
      comments[requestId]?.trim() || ''

    if (comment.length < 5) {
      setActionError(
        'La justification doit contenir au moins 5 caractères.',
      )

      return
    }

    const actionLabel =
      decision === 'APPROVED'
        ? 'approuver'
        : 'refuser'

    const confirmed = window.confirm(
      `Voulez-vous vraiment ${actionLabel} cette demande ?`,
    )

    if (!confirmed) {
      return
    }

    setActionLoadingId(requestId)
    setActionError('')
    setSuccessMessage('')

    try {
      await apiRequest(
        `/access-requests/${requestId}/manager-decision`,
        {
          method: 'POST',
          body: JSON.stringify({
            decision,
            comment,
          }),
        },
      )

      setRequests((currentRequests) =>
        currentRequests.map((request) =>
          request.id === requestId
            ? {
                ...request,
                status: decision,
                manager_comment: comment,
              }
            : request,
        ),
      )

      setComments((currentComments) => {
        const updatedComments = {
          ...currentComments,
        }

        delete updatedComments[requestId]

        return updatedComments
      })

      setSuccessMessage(
        decision === 'APPROVED'
          ? 'La demande a été approuvée.'
          : 'La demande a été refusée.',
      )
    } catch (error) {
      setActionError(
        error.message ||
          'Impossible d’enregistrer la décision.',
      )
    } finally {
      setActionLoadingId(null)
    }
  }

  const pendingRequests = requests.filter(
    (request) =>
      request.status === 'PENDING_MANAGER',
  )

  return (
    <section className="manager-requests-page">
      <header className="manager-requests-header">
        <div>
          <h1>Demandes à valider</h1>

          <p>
            Approuvez ou refusez les demandes
            d’accès des employés.
          </p>
        </div>

        <div className="manager-requests-summary">
          <span className="pending-count">
            {pendingRequests.length}{' '}
            demande(s) en attente
          </span>

          <button
            type="button"
            className="refresh-button"
            onClick={loadRequests}
            disabled={loading}
          >
            {loading
              ? 'Chargement...'
              : 'Actualiser'}
          </button>
        </div>
      </header>

      <ErrorMessage message={loadError} />
      <ErrorMessage message={actionError} />

      {successMessage && (
        <div
          className="success-message"
          role="status"
        >
          {successMessage}
        </div>
      )}

      {loading && (
        <LoadingSpinner message="Chargement des demandes..." />
      )}

      {!loading && loadError && (
        <button
          type="button"
          className="retry-button"
          onClick={loadRequests}
        >
          Réessayer
        </button>
      )}

      {!loading &&
        !loadError &&
        pendingRequests.length === 0 && (
          <div className="empty-state">
            <h2>Aucune demande en attente</h2>

            <p>
              Les nouvelles demandes des employés
              apparaîtront ici.
            </p>
          </div>
        )}

      {!loading &&
        !loadError &&
        pendingRequests.length > 0 && (
          <div className="manager-requests-list">
            {pendingRequests.map((request) => {
              const actionInProgress =
                actionLoadingId === request.id

              const comment =
                comments[request.id] || ''

              const commentIsValid =
                comment.trim().length >= 5

              return (
                <article
                  className="manager-request-card"
                  key={request.id}
                >
                  <div className="request-card-header">
                    <div>
                      <span className="request-number">
                        Demande n°{request.id}
                      </span>

                      <h2>
                        {getResourceName(
                          request.resource_id,
                        )}
                      </h2>
                    </div>

                    <StatusBadge
                      status={request.status}
                    />
                  </div>

                  <dl className="request-information">
                    <div>
                      <dt>Employé</dt>

                      <dd>
                        {request.requester_email ||
                          request.employee_email ||
                          request.user_email ||
                          'Non renseigné'}
                      </dd>
                    </div>

                    <div>
                      <dt>
                        Justification de l’employé
                      </dt>

                      <dd>
                        {request.justification ||
                          request.reason ||
                          'Non renseignée'}
                      </dd>
                    </div>

                    <div>
                      <dt>Date de début</dt>

                      <dd>
                        {formatDate(
                          request.start_date ||
                            request.valid_from,
                        )}
                      </dd>
                    </div>

                    <div>
                      <dt>Date de fin</dt>

                      <dd>
                        {formatDate(
                          request.end_date ||
                            request.valid_until,
                        )}
                      </dd>
                    </div>
                  </dl>

                  <div className="manager-comment-field">
                    <label
                      htmlFor={`manager-comment-${request.id}`}
                    >
                      Justification du manager
                    </label>

                    <textarea
                      id={`manager-comment-${request.id}`}
                      value={comment}
                      onChange={(event) =>
                        handleCommentChange(
                          request.id,
                          event.target.value,
                        )
                      }
                      placeholder="Expliquez pourquoi vous approuvez ou refusez cette demande..."
                      rows="4"
                      minLength="5"
                      maxLength="500"
                      disabled={actionInProgress}
                      required
                    />

                    <small
                      className={
                        commentIsValid
                          ? 'comment-counter valid'
                          : 'comment-counter invalid'
                      }
                    >
                      {comment.length}/500 caractères
                      {' — '}
                      minimum 5
                    </small>
                  </div>

                  <div className="request-actions">
                    <button
                      type="button"
                      className="approve-button"
                      disabled={
                        actionInProgress ||
                        !commentIsValid
                      }
                      onClick={() =>
                        handleDecision(
                          request.id,
                          'APPROVED',
                        )
                      }
                    >
                      {actionInProgress
                        ? 'Traitement...'
                        : 'Approuver'}
                    </button>

                    <button
                      type="button"
                      className="reject-button"
                      disabled={
                        actionInProgress ||
                        !commentIsValid
                      }
                      onClick={() =>
                        handleDecision(
                          request.id,
                          'REFUSED',
                        )
                      }
                    >
                      {actionInProgress
                        ? 'Traitement...'
                        : 'Refuser'}
                    </button>
                  </div>
                </article>
              )
            })}
          </div>
        )}
    </section>
  )
}

export default ManagerRequests