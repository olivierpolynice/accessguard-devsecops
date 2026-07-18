import {
  useCallback,
  useEffect,
  useState,
} from 'react'
import {
  Link,
  useOutletContext,
} from 'react-router-dom'
import ErrorMessage from '../components/ErrorMessage'
import LoadingSpinner from '../components/LoadingSpinner'
import StatusBadge from '../components/StatusBadge'
import { apiRequest } from '../services/api'
import './Dashboard.css'

const roleLabels = {
  employee: 'Employé',
  manager: 'Manager',
  it_admin: 'Administrateur IT',
  security_admin: 'Administrateur sécurité',
}

const auditActionLabels = {
  ACCESS_REQUEST_CREATED:
    'Demande d’accès créée',
  MANAGER_DECISION:
    'Décision du manager',
  ACCESS_GRANTED:
    'Accès attribué',
  ACCESS_REVOKED:
    'Accès révoqué',
  USER_CREATED:
    'Utilisateur créé',
  USER_ROLE_UPDATED:
    'Rôle mis à jour',
  USER_STATUS_UPDATED:
    'Statut utilisateur modifié',
}

function formatDateTime(value) {
  if (!value) {
    return 'Date inconnue'
  }

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return value
  }

  return new Intl.DateTimeFormat(
    'fr-FR',
    {
      dateStyle: 'short',
      timeStyle: 'short',
    },
  ).format(date)
}

function getAuditDate(event) {
  return (
    event.created_at ||
    event.timestamp ||
    event.date
  )
}

function getAuditUser(event) {
  return (
    event.user_email ||
    event.actor_email ||
    event.user ||
    'Système'
  )
}

function getAuditAction(action) {
  return (
    auditActionLabels[action] ||
    action ||
    'Action enregistrée'
  )
}

function DashboardCard({
  title,
  value,
  description,
  variant = 'blue',
  link,
  linkLabel,
}) {
  return (
    <article
      className={`dashboard-card dashboard-card-${variant}`}
    >
      <p className="dashboard-card-title">
        {title}
      </p>

      <strong className="dashboard-card-value">
        {value}
      </strong>

      <p className="dashboard-card-description">
        {description}
      </p>

      {link && linkLabel && (
        <Link
          className="dashboard-card-link"
          to={link}
        >
          {linkLabel}
        </Link>
      )}
    </article>
  )
}

function Dashboard() {
  const { user } = useOutletContext()

  const [dashboardData, setDashboardData] =
    useState({})
  const [loading, setLoading] =
    useState(true)
  const [error, setError] =
    useState('')

  const loadDashboard = useCallback(async () => {
    setLoading(true)
    setError('')

    try {
      if (user.role === 'employee') {
        const [
          resourcesData,
          requestsData,
          grantsData,
        ] = await Promise.all([
          apiRequest('/resources'),
          apiRequest('/access-requests'),
          apiRequest('/access-grants'),
        ])

        const resources =
          Array.isArray(resourcesData)
            ? resourcesData
            : []

        const requests =
          Array.isArray(requestsData)
            ? requestsData
            : []

        const grants =
          Array.isArray(grantsData)
            ? grantsData
            : []

        const pendingRequests =
          requests.filter(
            (request) =>
              request.status ===
              'PENDING_MANAGER',
          )

        const activeGrants =
          grants.filter(
            (grant) =>
              grant.status !== 'REVOKED' &&
              !grant.revoked_at,
          )

        setDashboardData({
          resources,
          requests,
          pendingRequests,
          activeGrants,
        })

        return
      }

      if (user.role === 'manager') {
        const [
          requestsData,
          resourcesData,
        ] = await Promise.all([
          apiRequest('/access-requests'),
          apiRequest('/resources'),
        ])

        const requests =
          Array.isArray(requestsData)
            ? requestsData
            : []

        const resources =
          Array.isArray(resourcesData)
            ? resourcesData
            : []

        const pendingRequests =
          requests.filter(
            (request) =>
              request.status ===
              'PENDING_MANAGER',
          )

        setDashboardData({
          requests,
          resources,
          pendingRequests,
        })

        return
      }

      if (user.role === 'it_admin') {
        const [
          requestsData,
          grantsData,
        ] = await Promise.all([
          apiRequest('/access-requests'),
          apiRequest('/access-grants'),
        ])

        const requests =
          Array.isArray(requestsData)
            ? requestsData
            : []

        const grants =
          Array.isArray(grantsData)
            ? grantsData
            : []

        const approvedRequests =
          requests.filter(
            (request) =>
              request.status === 'APPROVED',
          )

        const activeGrants =
          grants.filter(
            (grant) =>
              grant.status !== 'REVOKED' &&
              !grant.revoked_at,
          )

        const revokedGrants =
          grants.filter(
            (grant) =>
              grant.status === 'REVOKED' ||
              Boolean(grant.revoked_at),
          )

        setDashboardData({
          requests,
          grants,
          approvedRequests,
          activeGrants,
          revokedGrants,
        })

        return
      }

      if (user.role === 'security_admin') {
        const [
          usersData,
          auditData,
        ] = await Promise.all([
          apiRequest('/users'),
          apiRequest('/audit-logs'),
        ])

        const users =
          Array.isArray(usersData)
            ? usersData
            : []

        const auditLogs =
          Array.isArray(auditData)
            ? auditData
            : []

        const activeUsers =
          users.filter(
            (currentUser) =>
              currentUser.is_active,
          )

        const inactiveUsers =
          users.filter(
            (currentUser) =>
              !currentUser.is_active,
          )

        const recentAuditEvents =
          [...auditLogs]
            .sort((firstEvent, secondEvent) => {
              const firstDate = new Date(
                getAuditDate(firstEvent) || 0,
              )

              const secondDate = new Date(
                getAuditDate(secondEvent) || 0,
              )

              return secondDate - firstDate
            })
            .slice(0, 5)

        setDashboardData({
          users,
          auditLogs,
          activeUsers,
          inactiveUsers,
          recentAuditEvents,
        })

        return
      }

      setDashboardData({})
    } catch (loadError) {
      setDashboardData({})

      setError(
        loadError.message ||
          'Impossible de charger le tableau de bord.',
      )
    } finally {
      setLoading(false)
    }
  }, [user.role])

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      loadDashboard()
    }, 0)

    return () => {
      window.clearTimeout(timeoutId)
    }
  }, [loadDashboard])

  function getResourceName(resourceId) {
    const resource =
      dashboardData.resources?.find(
        (item) =>
          Number(item.id) ===
          Number(resourceId),
      )

    return (
      resource?.name ||
      `Ressource ${resourceId}`
    )
  }

  function renderEmployeeDashboard() {
    return (
      <>
        <div className="dashboard-grid">
          <DashboardCard
            title="Ressources disponibles"
            value={
              dashboardData.resources?.length || 0
            }
            description="Ressources accessibles dans le catalogue."
            variant="blue"
            link="/resources"
            linkLabel="Voir les ressources"
          />

          <DashboardCard
            title="Demandes en attente"
            value={
              dashboardData.pendingRequests
                ?.length || 0
            }
            description="Demandes en attente d’une décision."
            variant="yellow"
            link="/requests"
            linkLabel="Voir mes demandes"
          />

          <DashboardCard
            title="Accès actifs"
            value={
              dashboardData.activeGrants
                ?.length || 0
            }
            description="Autorisations actuellement actives."
            variant="green"
          />

          <DashboardCard
            title="Nouvelle demande"
            value="+"
            description="Demandez l’accès à une ressource."
            variant="purple"
            link="/requests"
            linkLabel="Créer une demande"
          />
        </div>

        <section className="dashboard-section">
          <div className="dashboard-section-header">
            <div>
              <h2>Mes demandes récentes</h2>

              <p>
                Suivez l’avancement de vos demandes.
              </p>
            </div>

            <Link
              className="dashboard-section-link"
              to="/requests"
            >
              Tout afficher
            </Link>
          </div>

          {dashboardData.requests?.length ? (
            <div className="dashboard-list">
              {dashboardData.requests
                .slice(0, 3)
                .map((request) => (
                  <article
                    className="dashboard-list-item"
                    key={request.id}
                  >
                    <div>
                      <strong>
                        {getResourceName(
                          request.resource_id,
                        )}
                      </strong>

                      <p>
                        {request.justification ||
                          request.reason ||
                          'Sans justification'}
                      </p>
                    </div>

                    <StatusBadge
                      status={request.status}
                    />
                  </article>
                ))}
            </div>
          ) : (
            <p className="dashboard-empty">
              Vous n’avez encore envoyé aucune demande.
            </p>
          )}
        </section>
      </>
    )
  }

  function renderManagerDashboard() {
    return (
      <>
        <div className="dashboard-grid">
          <DashboardCard
            title="Demandes en attente"
            value={
              dashboardData.pendingRequests
                ?.length || 0
            }
            description="Demandes nécessitant votre décision."
            variant="yellow"
            link="/manager-requests"
            linkLabel="Examiner les demandes"
          />

          <DashboardCard
            title="Demandes totales"
            value={
              dashboardData.requests?.length || 0
            }
            description="Ensemble des demandes enregistrées."
            variant="blue"
          />

          <DashboardCard
            title="Approuver"
            value="✓"
            description="Validez une demande justifiée."
            variant="green"
            link="/manager-requests"
            linkLabel="Ouvrir la validation"
          />

          <DashboardCard
            title="Refuser"
            value="×"
            description="Refusez une demande non conforme."
            variant="red"
            link="/manager-requests"
            linkLabel="Ouvrir la validation"
          />
        </div>

        <section className="dashboard-section">
          <div className="dashboard-section-header">
            <div>
              <h2>Demandes à examiner</h2>

              <p>
                Détail des demandes les plus récentes.
              </p>
            </div>

            <Link
              className="dashboard-section-link"
              to="/manager-requests"
            >
              Tout examiner
            </Link>
          </div>

          {dashboardData.pendingRequests?.length ? (
            <div className="dashboard-list">
              {dashboardData.pendingRequests
                .slice(0, 3)
                .map((request) => (
                  <article
                    className="dashboard-list-item"
                    key={request.id}
                  >
                    <div>
                      <strong>
                        {getResourceName(
                          request.resource_id,
                        )}
                      </strong>

                      <p>
                        {request.requester_email ||
                          request.employee_email ||
                          request.user_email ||
                          'Employé non renseigné'}
                      </p>

                      <small>
                        {request.justification ||
                          request.reason ||
                          'Sans justification'}
                      </small>
                    </div>

                    <Link
                      className="dashboard-action-button"
                      to="/manager-requests"
                    >
                      Traiter
                    </Link>
                  </article>
                ))}
            </div>
          ) : (
            <p className="dashboard-empty">
              Aucune demande n’attend de décision.
            </p>
          )}
        </section>
      </>
    )
  }

  function renderItAdminDashboard() {
    return (
      <>
        <div className="dashboard-grid">
          <DashboardCard
            title="Demandes approuvées"
            value={
              dashboardData.approvedRequests
                ?.length || 0
            }
            description="Demandes prêtes à être attribuées."
            variant="yellow"
            link="/grants"
            linkLabel="Attribuer les accès"
          />

          <DashboardCard
            title="Accès à attribuer"
            value={
              dashboardData.approvedRequests
                ?.length || 0
            }
            description="Attributions en attente de traitement."
            variant="blue"
            link="/grants"
            linkLabel="Gérer les attributions"
          />

          <DashboardCard
            title="Accès actifs"
            value={
              dashboardData.activeGrants
                ?.length || 0
            }
            description="Accès actuellement utilisables."
            variant="green"
            link="/grants"
            linkLabel="Voir les accès"
          />

          <DashboardCard
            title="Accès révoqués"
            value={
              dashboardData.revokedGrants
                ?.length || 0
            }
            description="Accès retirés aux utilisateurs."
            variant="red"
            link="/grants"
            linkLabel="Consulter l’historique"
          />
        </div>

        <section className="dashboard-callout">
          <div>
            <h2>Gestion des accès</h2>

            <p>
              Attribuez les demandes approuvées ou
              révoquez un accès devenu inutile.
            </p>
          </div>

          <Link
            className="dashboard-primary-button"
            to="/grants"
          >
            Ouvrir la gestion des accès
          </Link>
        </section>
      </>
    )
  }

  function renderSecurityDashboard() {
    return (
      <>
        <div className="dashboard-grid">
          <DashboardCard
            title="Utilisateurs"
            value={
              dashboardData.users?.length || 0
            }
            description="Comptes enregistrés dans AccessGuard."
            variant="blue"
            link="/users"
            linkLabel="Gérer les utilisateurs"
          />

          <DashboardCard
            title="Utilisateurs actifs"
            value={
              dashboardData.activeUsers
                ?.length || 0
            }
            description="Comptes autorisés à se connecter."
            variant="green"
            link="/users"
            linkLabel="Consulter les comptes"
          />

          <DashboardCard
            title="Utilisateurs inactifs"
            value={
              dashboardData.inactiveUsers
                ?.length || 0
            }
            description="Comptes actuellement désactivés."
            variant="red"
            link="/users"
            linkLabel="Gérer les statuts"
          />

          <DashboardCard
            title="Événements d’audit"
            value={
              dashboardData.auditLogs?.length || 0
            }
            description="Événements de sécurité enregistrés."
            variant="purple"
            link="/audit"
            linkLabel="Consulter l’audit"
          />
        </div>

        <div className="dashboard-security-layout">
          <section className="dashboard-section">
            <div className="dashboard-section-header">
              <div>
                <h2>Derniers événements d’audit</h2>

                <p>
                  Activité récente enregistrée par
                  AccessGuard.
                </p>
              </div>

              <Link
                className="dashboard-section-link"
                to="/audit"
              >
                Journal complet
              </Link>
            </div>

            {dashboardData.recentAuditEvents
              ?.length ? (
              <div className="dashboard-audit-list">
                {dashboardData.recentAuditEvents.map(
                  (event) => (
                    <article
                      className="dashboard-audit-item"
                      key={
                        event.id ||
                        `${getAuditDate(event)}-${event.action}`
                      }
                    >
                      <div>
                        <strong>
                          {getAuditAction(
                            event.action,
                          )}
                        </strong>

                        <p>
                          {getAuditUser(event)}
                        </p>
                      </div>

                      <time>
                        {formatDateTime(
                          getAuditDate(event),
                        )}
                      </time>
                    </article>
                  ),
                )}
              </div>
            ) : (
              <p className="dashboard-empty">
                Aucun événement récent.
              </p>
            )}
          </section>

          <section className="dashboard-monitoring-card">
            <div>
              <span className="monitoring-indicator">
                ●
              </span>

              <h2>Supervision</h2>

              <p>
                Accédez aux outils Grafana et
                Prometheus pour surveiller
                AccessGuard.
              </p>
            </div>

            <Link
              className="dashboard-primary-button"
              to="/monitoring"
            >
              Accéder au monitoring
            </Link>
          </section>
        </div>
      </>
    )
  }

  function renderDashboardByRole() {
    if (user.role === 'employee') {
      return renderEmployeeDashboard()
    }

    if (user.role === 'manager') {
      return renderManagerDashboard()
    }

    if (user.role === 'it_admin') {
      return renderItAdminDashboard()
    }

    if (user.role === 'security_admin') {
      return renderSecurityDashboard()
    }

    return (
      <ErrorMessage message="Rôle utilisateur inconnu." />
    )
  }

  return (
    <section className="page dashboard-page">
      <header className="dashboard-header">
        <div>
          <p className="dashboard-eyebrow">
            {roleLabels[user.role] ||
              user.role}
          </p>

          <h1>Tableau de bord</h1>

          <p>
            Bonjour {user.email}. Consultez le
            résumé de votre activité AccessGuard.
          </p>
        </div>

        <button
          type="button"
          className="dashboard-refresh-button"
          onClick={loadDashboard}
          disabled={loading}
        >
          {loading
            ? 'Chargement...'
            : 'Actualiser'}
        </button>
      </header>

      {loading && (
        <LoadingSpinner message="Chargement du tableau de bord..." />
      )}

      {!loading && error && (
        <ErrorMessage
          message={error}
          onRetry={loadDashboard}
        />
      )}

      {!loading &&
        !error &&
        renderDashboardByRole()}
    </section>
  )
}

export default Dashboard