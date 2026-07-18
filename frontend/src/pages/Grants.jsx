import { useEffect, useRef, useState } from 'react'
import ErrorMessage from '../components/ErrorMessage'
import LoadingSpinner from '../components/LoadingSpinner'
import SuccessMessage from '../components/SuccessMessage'
import StatusBadge from '../components/StatusBadge'
import { apiRequest } from '../services/api'
import './Grants.css'
import ConfirmDialog from '../components/ConfirmDialog'

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

function Grants() {
  const [grants, setGrants] = useState([])
  const [requests, setRequests] = useState([])
  const [resources, setResources] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const [showGrantForm, setShowGrantForm] =
    useState(false)
  const [selectedRequestId, setSelectedRequestId] =
    useState('')
  const [grantComment, setGrantComment] = useState('')
  const [revokeComments, setRevokeComments] =
    useState({})

  const [grantSubmitting, setGrantSubmitting] =
    useState(false)
  const [revokingId, setRevokingId] = useState(null)
  const [pendingRevokeId, setPendingRevokeId] =
    useState(null)
  const [actionError, setActionError] = useState('')
  const [successMessage, setSuccessMessage] =
    useState('')

  const grantSubmittingRef = useRef(false)
  const revokingRef = useRef(false)

  useEffect(() => {
    let cancelled = false

    Promise.all([
      apiRequest('/access-grants'),
      apiRequest('/access-requests'),
      apiRequest('/resources'),
    ])
      .then(
        ([grantsData, requestsData, resourcesData]) => {
          if (cancelled) {
            return
          }

          setGrants(
            Array.isArray(grantsData)
              ? grantsData
              : [],
          )

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
        },
      )
      .catch((loadError) => {
        if (!cancelled) {
          setError(
            loadError.message ||
              'Impossible de charger les accès attribués.',
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
      const [
        grantsData,
        requestsData,
        resourcesData,
      ] = await Promise.all([
        apiRequest('/access-grants'),
        apiRequest('/access-requests'),
        apiRequest('/resources'),
      ])

      setGrants(
        Array.isArray(grantsData)
          ? grantsData
          : [],
      )

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
    } catch (loadError) {
      setError(
        loadError.message ||
          'Impossible de charger les accès attribués.',
      )
    } finally {
      setLoading(false)
    }
  }

  function getResourceName(resourceId) {
    const resource = resources.find(
      (item) =>
        Number(item.id) === Number(resourceId),
    )

    return (
      resource?.name ||
      `Ressource ${resourceId}`
    )
  }

  function handleRevokeCommentChange(
    grantId,
    value,
  ) {
    setRevokeComments((currentComments) => ({
      ...currentComments,
      [grantId]: value,
    }))

    setActionError('')
    setSuccessMessage('')
  }

  function handleToggleGrantForm() {
    setShowGrantForm(
      (currentValue) => !currentValue,
    )

    setActionError('')
    setSuccessMessage('')
  }

  async function handleGrant(event) {
    event.preventDefault()

    if (grantSubmittingRef.current) {
      return
    }

    if (!selectedRequestId) {
      setActionError(
        'Sélectionnez une demande approuvée.',
      )
      return
    }

    const comment = grantComment.trim()

    if (comment.length < 5) {
      setActionError(
        'La justification de l’attribution doit contenir au moins 5 caractères.',
      )
      return
    }

    const confirmed = window.confirm(
      'Voulez-vous vraiment attribuer cet accès ?',
    )

    if (!confirmed) {
      return
    }

    grantSubmittingRef.current = true
    setGrantSubmitting(true)
    setActionError('')
    setSuccessMessage('')

    try {
      const createdGrant = await apiRequest(
        `/access-requests/${selectedRequestId}/grant`,
        {
          method: 'POST',
          body: JSON.stringify({
            comment,
          }),
        },
      )

      setGrants((currentGrants) => [
        createdGrant,
        ...currentGrants,
      ])

      setRequests((currentRequests) =>
        currentRequests.map((request) =>
          request.id === Number(selectedRequestId)
            ? {
                ...request,
                status: 'GRANTED',
              }
            : request,
        ),
      )

      setSelectedRequestId('')
      setGrantComment('')
      setShowGrantForm(false)

      setSuccessMessage(
        'Accès attribué avec succès.',
      )
    } catch (grantError) {
      setActionError(
        grantError.message ||
          'Impossible d’attribuer cet accès.',
      )
    } finally {
      grantSubmittingRef.current = false
      setGrantSubmitting(false)
    }
  }

  async function handleRevoke(grantId) {
    if (revokingRef.current) {
      return
    }

    const comment =
      revokeComments[grantId]?.trim() || ''

    if (comment.length < 5) {
      setActionError(
        'La justification de la révocation doit contenir au moins 5 caractères.',
      )
      return
    }

    revokingRef.current = true
    setRevokingId(grantId)
    setActionError('')
    setSuccessMessage('')

    try {
      const revokedGrant = await apiRequest(
        `/access-grants/${grantId}/revoke`,
        {
          method: 'POST',
          body: JSON.stringify({
            reason: comment,
          }),
        },
      )

      setGrants((currentGrants) =>
        currentGrants.map((grant) =>
          grant.id === grantId
            ? {
                ...grant,
                ...revokedGrant,
                status:
                  revokedGrant?.status ||
                  'REVOKED',
              }
            : grant,
        ),
      )

      setRevokeComments((currentComments) => {
        const updatedComments = {
          ...currentComments,
        }

        delete updatedComments[grantId]

        return updatedComments
      })

      setSuccessMessage(
        'Accès révoqué.',
      )
    } catch (revokeError) {
      setActionError(
        revokeError.message ||
          'Impossible de révoquer cet accès.',
      )
    } finally {
      revokingRef.current = false
      setRevokingId(null)
    }
  }

  function requestRevokeConfirmation(grantId) {
    const reason =
      revokeComments[grantId]?.trim() || ''

    if (reason.length < 5) {
      setActionError(
        'La justification de la révocation doit contenir au moins 5 caractères.',
      )
      return
    }

    setActionError('')
    setSuccessMessage('')
    setPendingRevokeId(grantId)
  }

  function cancelRevokeConfirmation() {
    if (revokingId !== null) {
      return
    }

    setPendingRevokeId(null)
  }

  async function confirmRevoke() {
    const grantId = pendingRevokeId

    if (grantId === null) {
      return
    }

    await handleRevoke(grantId)
    setPendingRevokeId(null)
  }

  const approvedRequests = requests.filter(
    (request) =>
      request.status === 'APPROVED',
  )

  const actionInProgress =
    grantSubmitting || revokingId !== null

  const grantCommentIsValid =
    grantComment.trim().length >= 5

  return (
    <section className="page grants-page">
      <div className="grants-header">
        <div>
          <h1>Gestion des accès</h1>

          <p>
            Attribuez ou révoquez les
            autorisations d’accès.
          </p>
        </div>

        <div className="user-actions">
          <button
            className="refresh-grants-button"
            type="button"
            onClick={handleReload}
            disabled={loading || actionInProgress}
          >
            {loading
              ? 'Chargement...'
              : 'Actualiser'}
          </button>

          <button
            className="new-grant-button"
            type="button"
            onClick={handleToggleGrantForm}
            disabled={loading || actionInProgress}
          >
            {showGrantForm
              ? 'Fermer le formulaire'
              : 'Attribuer un accès'}
          </button>
        </div>
      </div>

      <SuccessMessage
        message={successMessage}
        onClose={() => setSuccessMessage('')}
      />

      {actionError && (
        <ErrorMessage message={actionError} />
      )}

      {showGrantForm && (
        <form
          className="grant-form"
          onSubmit={handleGrant}
        >
          <h2>Attribuer un accès</h2>

          <div className="form-group">
            <label htmlFor="approved-request">
              Demande approuvée
            </label>

            <select
              id="approved-request"
              value={selectedRequestId}
              onChange={(event) => {
                setSelectedRequestId(
                  event.target.value,
                )
                setActionError('')
              }}
              disabled={grantSubmitting}
              required
            >
              <option value="">
                Sélectionnez une demande
              </option>

              {approvedRequests.map((request) => (
                <option
                  key={request.id}
                  value={request.id}
                >
                  Demande {request.id} —{' '}
                  {request.requester_email ||
                    request.employee_email ||
                    'Employé'}{' '}
                  —{' '}
                  {getResourceName(
                    request.resource_id,
                  )}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="grant-comment">
              Justification de l’attribution
            </label>

            <textarea
              id="grant-comment"
              value={grantComment}
              onChange={(event) => {
                setGrantComment(event.target.value)
                setActionError('')
              }}
              placeholder="Expliquez pourquoi cet accès est attribué..."
              rows="4"
              minLength="5"
              maxLength="500"
              disabled={grantSubmitting}
              required
            />

            <small
              className={
                grantCommentIsValid
                  ? 'comment-counter valid'
                  : 'comment-counter invalid'
              }
            >
              {grantComment.length}/500 caractères
              {' — '}
              minimum 5
            </small>
          </div>

          {approvedRequests.length === 0 && (
            <p className="empty-message">
              Aucune demande approuvée n’attend
              une attribution.
            </p>
          )}

          <button
            className="confirm-grant-button"
            type="submit"
            disabled={
              grantSubmitting ||
              revokingId !== null ||
              !selectedRequestId ||
              !grantCommentIsValid
            }
          >
            {grantSubmitting
              ? 'Attribution en cours...'
              : 'Confirmer l’attribution'}
          </button>
        </form>
      )}

      {loading && (
        <LoadingSpinner message="Chargement des accès..." />
      )}

      {error && (
        <ErrorMessage
          message={error}
          onRetry={handleReload}
        />
      )}

      {!loading &&
        !error &&
        grants.length === 0 && (
          <div className="empty-grants">
            <h2>Aucun accès attribué</h2>

            <p>
              Les accès attribués apparaîtront ici.
            </p>
          </div>
        )}

      {!loading &&
        !error &&
        grants.length > 0 && (
          <div className="table-container">
            <table className="grants-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Utilisateur</th>
                  <th>Ressource</th>
                  <th>Date d’attribution</th>
                  <th>Date d’expiration</th>
                  <th>Statut</th>
                  <th>Justification de révocation</th>
                  <th>Action</th>
                </tr>
              </thead>

              <tbody>
                {grants.map((grant) => {
                  const isRevoked =
                    grant.status === 'REVOKED' ||
                    Boolean(grant.revoked_at)

                  const isRevoking =
                    revokingId === grant.id

                  const revokeComment =
                    revokeComments[grant.id] || ''

                  const revokeCommentIsValid =
                    revokeComment.trim().length >= 5

                  return (
                    <tr key={grant.id}>
                      <td data-label="ID">
                        {grant.id}
                      </td>

                      <td data-label="Utilisateur">
                        {grant.user_email ||
                          grant.employee_email ||
                          grant.requester_email ||
                          grant.granted_to ||
                          'Utilisateur'}
                      </td>

                      <td data-label="Ressource">
                        {grant.resource_name ||
                          getResourceName(
                            grant.resource_id,
                          )}
                      </td>

                      <td data-label="Attribution">
                        {formatDate(
                          grant.granted_at ||
                            grant.created_at,
                        )}
                      </td>

                      <td data-label="Expiration">
                        {grant.expires_at
                          ? formatDate(
                              grant.expires_at,
                            )
                          : 'Sans expiration'}
                      </td>

                      <td data-label="Statut">
                        <StatusBadge
                          status={
                            isRevoked
                              ? 'REVOKED'
                              : 'ACTIVE'
                          }
                        />
                      </td>

                      <td data-label="Justification">
                        {isRevoked ? (
                          <span className="revoked-label">
                            Accès déjà révoqué
                          </span>
                        ) : (
                          <div className="revoke-comment-field">
                            <textarea
                              value={revokeComment}
                              onChange={(event) =>
                                handleRevokeCommentChange(
                                  grant.id,
                                  event.target.value,
                                )
                              }
                              placeholder="Motif de la révocation..."
                              rows="3"
                              minLength="5"
                              maxLength="500"
                              disabled={
                                actionInProgress
                              }
                            />

                            <small
                              className={
                                revokeCommentIsValid
                                  ? 'comment-counter valid'
                                  : 'comment-counter invalid'
                              }
                            >
                              {revokeComment.length}/500
                            </small>
                          </div>
                        )}
                      </td>

                      <td data-label="Action">
                        <button
                          className="revoke-grant-button"
                          type="button"
                          disabled={
                            isRevoked ||
                            grantSubmitting ||
                            revokingId !== null ||
                            !revokeCommentIsValid
                          }
                          onClick={() =>
                            requestRevokeConfirmation(
                              grant.id,
                            )
                          }
                        >
                          {isRevoking
                            ? 'Révocation...'
                            : isRevoked
                              ? 'Déjà révoqué'
                              : 'Révoquer'}
                        </button>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}

      <ConfirmDialog
        isOpen={pendingRevokeId !== null}
        title="Confirmer la révocation"
        message="Voulez-vous vraiment révoquer cet accès ? Cette action prendra effet immédiatement."
        cancelLabel="Annuler"
        confirmLabel="Confirmer la révocation"
        confirmVariant="danger"
        loading={revokingId !== null}
        onCancel={cancelRevokeConfirmation}
        onConfirm={confirmRevoke}
      />
    </section>
  )
}

export default Grants