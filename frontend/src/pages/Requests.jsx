import { useEffect, useRef, useState } from 'react'
import ErrorMessage from '../components/ErrorMessage'
import LoadingSpinner from '../components/LoadingSpinner'
import StatusBadge from '../components/StatusBadge'
import { apiRequest } from '../services/api'
import './Requests.css'

function formatDate(value) {
  if (!value) {
    return 'Non renseignée'
  }

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return 'Date invalide'
  }

  return new Intl.DateTimeFormat('fr-FR').format(date)
}

function Requests() {
  const [requests, setRequests] = useState([])
  const [resources, setResources] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const [showForm, setShowForm] = useState(false)
  const [resourceId, setResourceId] = useState('')
  const [reason, setReason] = useState('')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')

  const [submitting, setSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState('')
  const [successMessage, setSuccessMessage] =
    useState('')

  const submittingRef = useRef(false)

  useEffect(() => {
    let cancelled = false

    Promise.all([
      apiRequest('/access-requests'),
      apiRequest('/resources'),
    ])
      .then(([requestsData, resourcesData]) => {
        if (!cancelled) {
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

          setError('')
        }
      })
      .catch((requestError) => {
        if (!cancelled) {
          setError(
            requestError.message ||
              'Impossible de charger les demandes d’accès.',
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
      const [requestsData, resourcesData] =
        await Promise.all([
          apiRequest('/access-requests'),
          apiRequest('/resources'),
        ])

      setRequests(
        Array.isArray(requestsData) ? requestsData : [],
      )

      setResources(
        Array.isArray(resourcesData) ? resourcesData : [],
      )
    } catch (requestError) {
      setError(
        requestError.message ||
          'Impossible de charger les demandes d’accès.',
      )
    } finally {
      setLoading(false)
    }
  }

  async function handleSubmit(event) {
    event.preventDefault()

    if (submittingRef.current) {
      return
    }

    setSubmitError('')
    setSuccessMessage('')

    if (!resourceId) {
      setSubmitError('Sélectionnez une ressource.')
      return
    }

    if (reason.trim().length < 10) {
      setSubmitError(
        'Le motif doit contenir au moins 10 caractères.',
      )
      return
    }

    if (!startDate || !endDate) {
      setSubmitError(
        'Indiquez une date de début et une date de fin.',
      )
      return
    }

    if (endDate < startDate) {
      setSubmitError(
        'La date de fin doit être postérieure ou égale à la date de début.',
      )
      return
    }

    submittingRef.current = true
    setSubmitting(true)

    try {
      const createdRequest = await apiRequest(
        '/access-requests',
        {
          method: 'POST',
          body: JSON.stringify({
            resource_id: Number(resourceId),
            reason: reason.trim(),
            start_date: startDate,
            end_date: endDate,
          }),
        },
      )

      setRequests((currentRequests) => [
        createdRequest,
        ...currentRequests,
      ])

      setResourceId('')
      setReason('')
      setStartDate('')
      setEndDate('')
      setShowForm(false)

      setSuccessMessage(
        'Votre demande d’accès a bien été créée.',
      )
    } catch (requestError) {
      setSubmitError(
        requestError.message ||
          'Impossible de créer la demande d’accès.',
      )
    } finally {
      submittingRef.current = false
      setSubmitting(false)
    }
  }

  function handleToggleForm() {
    setShowForm((currentValue) => !currentValue)
    setSubmitError('')
    setSuccessMessage('')
  }

  function getResourceName(selectedResourceId) {
    const resource = resources.find(
      (item) => item.id === selectedResourceId,
    )

    return (
      resource?.name ||
      `Ressource ${selectedResourceId}`
    )
  }

  return (
    <section className="page">
      <div className="requests-header">
        <div>
          <h1>Mes demandes d’accès</h1>

          <p>
            Créez et suivez vos demandes d’accès.
          </p>
        </div>

        <div className="user-actions">
          <button
            className="request-details-button"
            type="button"
            onClick={handleReload}
            disabled={loading || submitting}
          >
            {loading ? 'Chargement...' : 'Actualiser'}
          </button>

          <button
            className="new-request-button"
            type="button"
            onClick={handleToggleForm}
            disabled={loading || submitting}
          >
            {showForm
              ? 'Fermer le formulaire'
              : 'Nouvelle demande'}
          </button>
        </div>
      </div>

      {successMessage && (
        <div
          className="success-message"
          role="status"
        >
          {successMessage}
        </div>
      )}

      {showForm && (
        <form
          className="request-form"
          onSubmit={handleSubmit}
          noValidate
        >
          <div className="form-group">
            <label htmlFor="request-resource">
              Ressource demandée
            </label>

            <select
              id="request-resource"
              value={resourceId}
              onChange={(event) => {
                setResourceId(event.target.value)
                setSubmitError('')
              }}
              disabled={submitting}
            >
              <option value="">
                Sélectionnez une ressource
              </option>

              {resources
                .filter(
                  (resource) =>
                    resource.is_active !== false,
                )
                .map((resource) => (
                  <option
                    key={resource.id}
                    value={resource.id}
                  >
                    {resource.name}
                  </option>
                ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="request-reason">
              Motif de la demande
            </label>

            <textarea
              id="request-reason"
              value={reason}
              onChange={(event) => {
                setReason(event.target.value)
                setSubmitError('')
              }}
              placeholder="Expliquez pourquoi cet accès est nécessaire."
              rows="4"
              disabled={submitting}
            />
          </div>

          <div className="request-date-fields">
            <div className="form-group">
              <label htmlFor="request-start-date">
                Date de début
              </label>

              <input
                id="request-start-date"
                type="date"
                value={startDate}
                onChange={(event) => {
                  const selectedDate =
                    event.target.value

                  setStartDate(selectedDate)
                  setSubmitError('')

                  if (
                    endDate &&
                    endDate < selectedDate
                  ) {
                    setEndDate('')
                  }
                }}
                disabled={submitting}
              />
            </div>

            <div className="form-group">
              <label htmlFor="request-end-date">
                Date de fin
              </label>

              <input
                id="request-end-date"
                type="date"
                value={endDate}
                min={startDate || undefined}
                onChange={(event) => {
                  setEndDate(event.target.value)
                  setSubmitError('')
                }}
                disabled={submitting}
              />
            </div>
          </div>

          {submitError && (
            <ErrorMessage message={submitError} />
          )}

          <button
            className="new-request-button"
            type="submit"
            disabled={submitting}
          >
            {submitting
              ? 'Création en cours...'
              : 'Valider la demande'}
          </button>
        </form>
      )}

      {loading && (
        <LoadingSpinner message="Chargement des demandes..." />
      )}

      {error && (
        <ErrorMessage
          message={error}
          onRetry={handleReload}
        />
      )}

      {!loading &&
        !error &&
        requests.length === 0 && (
          <p>
            Vous n’avez aucune demande d’accès.
          </p>
        )}

      {!loading &&
        !error &&
        requests.length > 0 && (
          <div className="table-container">
            <table className="requests-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Ressource</th>
                  <th>Motif</th>
                  <th>Début</th>
                  <th>Fin</th>
                  <th>Statut</th>
                  <th>Action</th>
                </tr>
              </thead>

              <tbody>
                {requests.map((request) => (
                  <tr key={request.id}>
                    <td>{request.id}</td>

                    <td>
                      {request.resource_name ||
                        getResourceName(
                          request.resource_id,
                        )}
                    </td>

                    <td>
                      {request.reason ||
                        request.justification ||
                        'Non renseigné'}
                    </td>

                    <td>
                      {formatDate(
                        request.start_date,
                      )}
                    </td>

                    <td>
                      {formatDate(
                        request.end_date,
                      )}
                    </td>

                    <td>
                      <StatusBadge
                        status={request.status}
                      />
                    </td>

                    <td>
                      <button
                        className="request-details-button"
                        type="button"
                        disabled={submitting}
                      >
                        Voir
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

export default Requests