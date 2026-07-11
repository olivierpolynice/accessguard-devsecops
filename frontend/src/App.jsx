import { useEffect, useState } from "react";

const API_URL = "http://127.0.0.1:8000";

const TOKEN_KEY = "accessguard_token";
const ROLE_KEY = "accessguard_role";
const EMAIL_KEY = "accessguard_email";

const emptyRequestForm = {
  resourceId: null,
  resourceName: "",
  reason: "",
  startDate: "",
  endDate: "",
};

function App() {
  const [email, setEmail] = useState(
    "alice.employee@asteriatech.local"
  );
  const [password, setPassword] = useState("AccessGuard123!");
  const [user, setUser] = useState(null);

  const [resources, setResources] = useState([]);
  const [requests, setRequests] = useState([]);
  const [grants, setGrants] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);

  const [requestForm, setRequestForm] =
    useState(emptyRequestForm);

  const [managerComments, setManagerComments] = useState({});
  const [grantComments, setGrantComments] = useState({});
  const [revokeReasons, setRevokeReasons] = useState({});

  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const [loadingId, setLoadingId] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem(TOKEN_KEY);
    const role = localStorage.getItem(ROLE_KEY);
    const savedEmail = localStorage.getItem(EMAIL_KEY);

    if (token && role && savedEmail) {
      setUser({
        email: savedEmail,
        role,
      });

      loadDashboard(token, role);
    }
  }, []);

  function getError(data, status) {
    if (typeof data?.detail === "string") {
      return data.detail;
    }

    if (Array.isArray(data?.detail)) {
      return data.detail
        .map((item) => item.msg)
        .join(", ");
    }

    return `Erreur HTTP ${status}`;
  }

  function notify(text, error = false) {
    setMessage(text);
    setIsError(error);
  }

  async function api(path, options = {}) {
    const token = localStorage.getItem(TOKEN_KEY);

    const response = await fetch(`${API_URL}${path}`, {
      ...options,
      headers: {
        ...(options.body
          ? { "Content-Type": "application/json" }
          : {}),
        ...(token
          ? { Authorization: `Bearer ${token}` }
          : {}),
        ...options.headers,
      },
    });

    let data = null;

    try {
      data = await response.json();
    } catch {
      data = null;
    }

    if (!response.ok) {
      throw new Error(getError(data, response.status));
    }

    return data;
  }

  async function loadDashboard(token, role) {
    try {
      setResources([]);
      setRequests([]);
      setGrants([]);
      setAuditLogs([]);

      if (role === "employee") {
        const [resourceResponse, requestResponse] =
          await Promise.all([
            fetch(`${API_URL}/resources`, {
              headers: {
                Authorization: `Bearer ${token}`,
              },
            }),
            fetch(`${API_URL}/access-requests`, {
              headers: {
                Authorization: `Bearer ${token}`,
              },
            }),
          ]);

        const resourceData = await resourceResponse.json();
        const requestData = await requestResponse.json();

        if (!resourceResponse.ok) {
          throw new Error(
            getError(resourceData, resourceResponse.status)
          );
        }

        if (!requestResponse.ok) {
          throw new Error(
            getError(requestData, requestResponse.status)
          );
        }

        setResources(resourceData);
        setRequests(requestData);
        return;
      }

      if (role === "manager") {
        const requestData = await api("/access-requests");
        setRequests(requestData);
        return;
      }

      if (role === "it_admin") {
        const [requestData, grantData] = await Promise.all([
          api("/access-requests"),
          api("/access-grants"),
        ]);

        setRequests(requestData);
        setGrants(grantData);
        return;
      }

      if (role === "security_admin") {
        const [requestData, grantData, auditData] =
          await Promise.all([
            api("/access-requests"),
            api("/access-grants"),
            api("/audit-logs"),
          ]);

        setRequests(requestData);
        setGrants(grantData);
        setAuditLogs(auditData);
        return;
      }

      notify(`Rôle inconnu : ${role}`, true);
    } catch (error) {
      notify(
        `Chargement du tableau de bord impossible : ${error.message}`,
        true
      );
    }
  }

  async function handleLogin(event) {
    event.preventDefault();
    setLoadingId("login");

    try {
      const response = await fetch(
        `${API_URL}/auth/login`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email: email.trim(),
            password,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          getError(data, response.status)
        );
      }

      localStorage.setItem(
        TOKEN_KEY,
        data.access_token
      );
      localStorage.setItem(ROLE_KEY, data.role);
      localStorage.setItem(EMAIL_KEY, data.email);

      setUser({
        email: data.email,
        role: data.role,
      });

      notify("Connexion réussie.");

      await loadDashboard(
        data.access_token,
        data.role
      );
    } catch (error) {
      notify(
        `Connexion impossible : ${error.message}`,
        true
      );
    } finally {
      setLoadingId(null);
    }
  }

  function logout() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(ROLE_KEY);
    localStorage.removeItem(EMAIL_KEY);

    setUser(null);
    setResources([]);
    setRequests([]);
    setGrants([]);
    setAuditLogs([]);

    setRequestForm(emptyRequestForm);
    setManagerComments({});
    setGrantComments({});
    setRevokeReasons({});

    notify("Déconnexion réussie.");
  }

  function openRequestForm(resource) {
    setRequestForm({
      resourceId: resource.id,
      resourceName: resource.name,
      reason: "",
      startDate: new Date()
        .toISOString()
        .slice(0, 10),
      endDate: "",
    });

    notify("");
  }

  async function createRequest(event) {
    event.preventDefault();
    setLoadingId("create-request");

    try {
      await api("/access-requests", {
        method: "POST",
        body: JSON.stringify({
          resource_id: requestForm.resourceId,
          reason: requestForm.reason.trim(),
          start_date: requestForm.startDate,
          end_date: requestForm.endDate,
        }),
      });

      setRequestForm(emptyRequestForm);

      const requestData = await api(
        "/access-requests"
      );

      setRequests(requestData);
      notify("Demande d’accès créée.");
    } catch (error) {
      notify(
        `Création impossible : ${error.message}`,
        true
      );
    } finally {
      setLoadingId(null);
    }
  }

  async function managerDecision(
    requestId,
    decision
  ) {
    const comment =
      managerComments[requestId]?.trim();

    if (!comment) {
      notify(
        "Ajoutez un commentaire manager.",
        true
      );
      return;
    }

    setLoadingId(`decision-${requestId}`);

    try {
      await api(
        `/access-requests/${requestId}/manager-decision`,
        {
          method: "POST",
          body: JSON.stringify({
            decision,
            comment,
          }),
        }
      );

      const requestData = await api(
        "/access-requests"
      );

      setRequests(requestData);

      setManagerComments((previous) => ({
        ...previous,
        [requestId]: "",
      }));

      notify(
        decision === "APPROVED"
          ? `Demande #${requestId} approuvée.`
          : `Demande #${requestId} refusée.`
      );
    } catch (error) {
      notify(
        `Décision impossible : ${error.message}`,
        true
      );
    } finally {
      setLoadingId(null);
    }
  }

  async function grantAccess(requestId) {
    const comment =
      grantComments[requestId]?.trim();

    if (!comment) {
      notify(
        "Ajoutez un commentaire d’attribution.",
        true
      );
      return;
    }

    setLoadingId(`grant-${requestId}`);

    try {
      await api(
        `/access-requests/${requestId}/grant`,
        {
          method: "POST",
          body: JSON.stringify({
            comment,
          }),
        }
      );

      const [requestData, grantData] =
        await Promise.all([
          api("/access-requests"),
          api("/access-grants"),
        ]);

      setRequests(requestData);
      setGrants(grantData);

      setGrantComments((previous) => ({
        ...previous,
        [requestId]: "",
      }));

      notify(
        `Accès attribué pour la demande #${requestId}.`
      );
    } catch (error) {
      notify(
        `Attribution impossible : ${error.message}`,
        true
      );
    } finally {
      setLoadingId(null);
    }
  }

  async function revokeAccess(grantId) {
    const reason =
      revokeReasons[grantId]?.trim();

    if (!reason) {
      notify(
        "Ajoutez un motif de révocation.",
        true
      );
      return;
    }

    setLoadingId(`revoke-${grantId}`);

    try {
      await api(
        `/access-grants/${grantId}/revoke`,
        {
          method: "POST",
          body: JSON.stringify({
            reason,
          }),
        }
      );

      const grantData = await api(
        "/access-grants"
      );

      setGrants(grantData);

      setRevokeReasons((previous) => ({
        ...previous,
        [grantId]: "",
      }));

      notify(`Accès #${grantId} révoqué.`);
    } catch (error) {
      notify(
        `Révocation impossible : ${error.message}`,
        true
      );
    } finally {
      setLoadingId(null);
    }
  }

  async function refreshSecurityDashboard() {
    setLoadingId("refresh-security");

    try {
      const [requestData, grantData, auditData] =
        await Promise.all([
          api("/access-requests"),
          api("/access-grants"),
          api("/audit-logs"),
        ]);

      setRequests(requestData);
      setGrants(grantData);
      setAuditLogs(auditData);

      notify(
        "Données de sécurité actualisées."
      );
    } catch (error) {
      notify(
        `Actualisation impossible : ${error.message}`,
        true
      );
    } finally {
      setLoadingId(null);
    }
  }

  const pendingRequests = requests.filter(
    (request) =>
      request.status === "PENDING_MANAGER"
  );

  const approvedRequests = requests.filter(
    (request) =>
      request.status === "APPROVED"
  );

  const activeGrants = grants.filter(
    (grant) => grant.status === "ACTIVE"
  );

  const revokedGrants = grants.filter(
    (grant) => grant.status === "REVOKED"
  );

  return (
    <main style={styles.page}>
      <section style={styles.container}>
        <header style={styles.header}>
          <div>
            <h1 style={styles.title}>
              AccessGuard
            </h1>

            <p style={styles.subtitle}>
              Gouvernance des accès AsteriaTech
            </p>
          </div>

          {user && (
            <button
              type="button"
              onClick={logout}
              style={styles.logoutButton}
            >
              Se déconnecter
            </button>
          )}
        </header>

        {!user ? (
          <section style={styles.card}>
            <h2>Authentification sécurisée</h2>

            <form
              onSubmit={handleLogin}
              style={styles.form}
            >
              <label style={styles.label}>
                Adresse e-mail

                <input
                  type="email"
                  value={email}
                  onChange={(event) =>
                    setEmail(event.target.value)
                  }
                  style={styles.input}
                  required
                />
              </label>

              <label style={styles.label}>
                Mot de passe

                <input
                  type="password"
                  value={password}
                  onChange={(event) =>
                    setPassword(
                      event.target.value
                    )
                  }
                  style={styles.input}
                  required
                />
              </label>

              <button
                type="submit"
                style={styles.primaryButton}
                disabled={
                  loadingId === "login"
                }
              >
                {loadingId === "login"
                  ? "Connexion..."
                  : "Se connecter"}
              </button>
            </form>
          </section>
        ) : (
          <>
            <section style={styles.sessionCard}>
              <h2>Session active</h2>

              <p>
                <strong>Utilisateur :</strong>{" "}
                {user.email}
              </p>

              <p>
                <strong>Rôle :</strong>{" "}
                {user.role}
              </p>
            </section>

            {user.role === "employee" && (
              <>
                <SectionTitle title="Ressources disponibles" />

                {resources.length === 0 ? (
                  <p style={styles.empty}>
                    Aucune ressource disponible.
                  </p>
                ) : (
                  <div style={styles.grid}>
                    {resources.map(
                      (resource) => (
                        <article
                          key={resource.id}
                          style={styles.itemCard}
                        >
                          <h3>
                            {resource.name}
                          </h3>

                          <p>
                            {
                              resource.description
                            }
                          </p>

                          <p>
                            <strong>
                              Sensibilité :
                            </strong>{" "}
                            {
                              resource.sensitivity
                            }
                          </p>

                          <button
                            type="button"
                            style={
                              styles.requestButton
                            }
                            onClick={() =>
                              openRequestForm(
                                resource
                              )
                            }
                          >
                            Demander l’accès
                          </button>
                        </article>
                      )
                    )}
                  </div>
                )}

                {requestForm.resourceId && (
                  <section style={styles.card}>
                    <h2>
                      Nouvelle demande —{" "}
                      {
                        requestForm.resourceName
                      }
                    </h2>

                    <form
                      onSubmit={createRequest}
                      style={styles.form}
                    >
                      <textarea
                        placeholder="Justification"
                        value={
                          requestForm.reason
                        }
                        onChange={(event) =>
                          setRequestForm({
                            ...requestForm,
                            reason:
                              event.target.value,
                          })
                        }
                        style={styles.textarea}
                        required
                      />

                      <label style={styles.label}>
                        Date de début

                        <input
                          type="date"
                          value={
                            requestForm.startDate
                          }
                          onChange={(event) =>
                            setRequestForm({
                              ...requestForm,
                              startDate:
                                event.target.value,
                            })
                          }
                          style={styles.input}
                          required
                        />
                      </label>

                      <label style={styles.label}>
                        Date de fin

                        <input
                          type="date"
                          value={
                            requestForm.endDate
                          }
                          min={
                            requestForm.startDate
                          }
                          onChange={(event) =>
                            setRequestForm({
                              ...requestForm,
                              endDate:
                                event.target.value,
                            })
                          }
                          style={styles.input}
                          required
                        />
                      </label>

                      <button
                        type="submit"
                        style={
                          styles.primaryButton
                        }
                        disabled={
                          loadingId ===
                          "create-request"
                        }
                      >
                        {loadingId ===
                        "create-request"
                          ? "Envoi..."
                          : "Envoyer la demande"}
                      </button>
                    </form>
                  </section>
                )}

                <SectionTitle title="Mes demandes" />

                {requests.length === 0 ? (
                  <p style={styles.empty}>
                    Aucune demande enregistrée.
                  </p>
                ) : (
                  <RequestCards
                    requests={requests}
                  />
                )}
              </>
            )}

            {user.role === "manager" && (
              <>
                <SectionTitle title="Demandes à valider" />

                {pendingRequests.length ===
                0 ? (
                  <p style={styles.empty}>
                    Aucune demande en attente de
                    validation.
                  </p>
                ) : (
                  pendingRequests.map(
                    (request) => (
                      <article
                        key={request.id}
                        style={styles.itemCard}
                      >
                        <RequestDetails
                          request={request}
                        />

                        <textarea
                          placeholder="Commentaire du manager"
                          value={
                            managerComments[
                              request.id
                            ] || ""
                          }
                          onChange={(event) =>
                            setManagerComments(
                              {
                                ...managerComments,
                                [request.id]:
                                  event.target
                                    .value,
                              }
                            )
                          }
                          style={styles.textarea}
                        />

                        <div
                          style={
                            styles.buttonRow
                          }
                        >
                          <button
                            type="button"
                            style={
                              styles.approveButton
                            }
                            onClick={() =>
                              managerDecision(
                                request.id,
                                "APPROVED"
                              )
                            }
                            disabled={
                              loadingId ===
                              `decision-${request.id}`
                            }
                          >
                            Approuver
                          </button>

                          <button
                            type="button"
                            style={
                              styles.rejectButton
                            }
                            onClick={() =>
                              managerDecision(
                                request.id,
                                "REJECTED"
                              )
                            }
                            disabled={
                              loadingId ===
                              `decision-${request.id}`
                            }
                          >
                            Refuser
                          </button>
                        </div>
                      </article>
                    )
                  )
                )}

                <SectionTitle title="Toutes les demandes" />

                {requests.length === 0 ? (
                  <p style={styles.empty}>
                    Aucune demande enregistrée.
                  </p>
                ) : (
                  <RequestCards
                    requests={requests}
                  />
                )}
              </>
            )}

            {user.role === "it_admin" && (
              <>
                <SectionTitle title="Demandes approuvées" />

                {approvedRequests.length ===
                0 ? (
                  <p style={styles.empty}>
                    Aucune demande approuvée à
                    traiter.
                  </p>
                ) : (
                  approvedRequests.map(
                    (request) => (
                      <article
                        key={request.id}
                        style={styles.itemCard}
                      >
                        <RequestDetails
                          request={request}
                        />

                        <textarea
                          placeholder="Commentaire d’attribution"
                          value={
                            grantComments[
                              request.id
                            ] || ""
                          }
                          onChange={(event) =>
                            setGrantComments({
                              ...grantComments,
                              [request.id]:
                                event.target
                                  .value,
                            })
                          }
                          style={styles.textarea}
                        />

                        <button
                          type="button"
                          style={
                            styles.grantButton
                          }
                          onClick={() =>
                            grantAccess(
                              request.id
                            )
                          }
                          disabled={
                            loadingId ===
                            `grant-${request.id}`
                          }
                        >
                          {loadingId ===
                          `grant-${request.id}`
                            ? "Attribution..."
                            : "Attribuer l’accès"}
                        </button>
                      </article>
                    )
                  )
                )}

                <SectionTitle title="Accès attribués" />

                {grants.length === 0 ? (
                  <p style={styles.empty}>
                    Aucun accès attribué.
                  </p>
                ) : (
                  grants.map((grant) => (
                    <article
                      key={grant.id}
                      style={styles.itemCard}
                    >
                      <GrantDetails
                        grant={grant}
                      />

                      {grant.status ===
                        "ACTIVE" && (
                        <>
                          <textarea
                            placeholder="Motif de révocation"
                            value={
                              revokeReasons[
                                grant.id
                              ] || ""
                            }
                            onChange={(
                              event
                            ) =>
                              setRevokeReasons(
                                {
                                  ...revokeReasons,
                                  [grant.id]:
                                    event.target
                                      .value,
                                }
                              )
                            }
                            style={
                              styles.textarea
                            }
                          />

                          <button
                            type="button"
                            style={
                              styles.revokeButton
                            }
                            onClick={() =>
                              revokeAccess(
                                grant.id
                              )
                            }
                            disabled={
                              loadingId ===
                              `revoke-${grant.id}`
                            }
                          >
                            {loadingId ===
                            `revoke-${grant.id}`
                              ? "Révocation..."
                              : "Révoquer l’accès"}
                          </button>
                        </>
                      )}
                    </article>
                  ))
                )}
              </>
            )}

            {user.role ===
              "security_admin" && (
              <>
                <div
                  style={
                    styles.securityHeader
                  }
                >
                  <SectionTitle title="Tableau de bord sécurité" />

                  <button
                    type="button"
                    style={
                      styles.refreshButton
                    }
                    onClick={
                      refreshSecurityDashboard
                    }
                    disabled={
                      loadingId ===
                      "refresh-security"
                    }
                  >
                    {loadingId ===
                    "refresh-security"
                      ? "Actualisation..."
                      : "Actualiser"}
                  </button>
                </div>

                <section
                  style={
                    styles.securitySummary
                  }
                >
                  <SummaryCard
                    value={requests.length}
                    label="Demandes"
                  />

                  <SummaryCard
                    value={activeGrants.length}
                    label="Accès actifs"
                  />

                  <SummaryCard
                    value={revokedGrants.length}
                    label="Accès révoqués"
                  />

                  <SummaryCard
                    value={auditLogs.length}
                    label="Événements d’audit"
                  />
                </section>

                <SectionTitle title="Demandes d’accès" />

                {requests.length === 0 ? (
                  <p style={styles.empty}>
                    Aucune demande enregistrée.
                  </p>
                ) : (
                  requests.map((request) => (
                    <article
                      key={request.id}
                      style={styles.itemCard}
                    >
                      <RequestDetails
                        request={request}
                      />
                    </article>
                  ))
                )}

                <SectionTitle title="Accès attribués et révoqués" />

                {grants.length === 0 ? (
                  <p style={styles.empty}>
                    Aucun accès enregistré.
                  </p>
                ) : (
                  grants.map((grant) => (
                    <article
                      key={grant.id}
                      style={styles.itemCard}
                    >
                      <GrantDetails
                        grant={grant}
                      />
                    </article>
                  ))
                )}

                <SectionTitle title="Journaux d’audit" />

                {auditLogs.length === 0 ? (
                  <p style={styles.empty}>
                    Aucun événement d’audit
                    enregistré.
                  </p>
                ) : (
                  auditLogs.map(
                    (log, index) => (
                      <AuditLogCard
                        key={
                          log.id ??
                          `${getAuditDate(
                            log
                          )}-${index}`
                        }
                        log={log}
                      />
                    )
                  )
                )}
              </>
            )}
          </>
        )}

        {message && (
          <p
            style={{
              ...styles.message,
              color: isError
                ? "#ff7b72"
                : "#7ee787",
            }}
          >
            {message}
          </p>
        )}
      </section>
    </main>
  );
}

function SectionTitle({ title }) {
  return (
    <section style={styles.sectionTitle}>
      <h2>{title}</h2>
    </section>
  );
}

function SummaryCard({ value, label }) {
  return (
    <article style={styles.summaryCard}>
      <strong style={styles.summaryValue}>
        {value}
      </strong>

      <span style={styles.summaryLabel}>
        {label}
      </span>
    </article>
  );
}

function StatusBadge({ status }) {
  const normalizedStatus =
    status?.toUpperCase() || "INCONNU";

  let statusStyle = styles.defaultStatus;

  if (
    normalizedStatus === "ACTIVE" ||
    normalizedStatus === "APPROVED"
  ) {
    statusStyle = styles.activeStatus;
  }

  if (
    normalizedStatus === "REVOKED" ||
    normalizedStatus === "REJECTED"
  ) {
    statusStyle = styles.revokedStatus;
  }

  if (
    normalizedStatus === "PENDING" ||
    normalizedStatus ===
      "PENDING_MANAGER"
  ) {
    statusStyle = styles.pendingStatus;
  }

  return (
    <span style={statusStyle}>
      {normalizedStatus}
    </span>
  );
}

function RequestDetails({ request }) {
  return (
    <>
      <h3>
        {request.resource_name ??
          `Ressource #${request.resource_id}`}
      </h3>

      <p>
        <strong>Demande :</strong> #
        {request.id}
      </p>

      <p>
        <strong>Employé :</strong>{" "}
        {request.requester_email ??
          request.employee_email ??
          "Non précisé"}
      </p>

      <p>
        <strong>Justification :</strong>{" "}
        {request.reason ??
          request.justification ??
          "Non précisée"}
      </p>

      <p>
        <strong>Période :</strong>{" "}
        {request.start_date ?? "Non précisée"}{" "}
        au{" "}
        {request.end_date ?? "Non précisée"}
      </p>

      <p>
        <strong>Statut :</strong>{" "}
        <StatusBadge
          status={request.status}
        />
      </p>

      {request.manager_comment && (
        <p>
          <strong>
            Commentaire manager :
          </strong>{" "}
          {request.manager_comment}
        </p>
      )}
    </>
  );
}

function RequestCards({ requests }) {
  return requests.map((request) => (
    <article
      key={request.id}
      style={styles.itemCard}
    >
      <RequestDetails request={request} />
    </article>
  ));
}

function GrantDetails({ grant }) {
  return (
    <>
      <h3>
        {grant.resource_name ??
          `Ressource #${grant.resource_id}`}
      </h3>

      <p>
        <strong>Accès :</strong> #{grant.id}
      </p>

      <p>
        <strong>Utilisateur :</strong>{" "}
        {grant.requester_email ??
          grant.user_email ??
          "Non précisé"}
      </p>

      <p>
        <strong>Statut :</strong>{" "}
        <StatusBadge status={grant.status} />
      </p>

      <p>
        <strong>Expiration :</strong>{" "}
        {grant.expires_at ??
          grant.expiration_date ??
          "Non précisée"}
      </p>

      {grant.granted_at && (
        <p>
          <strong>Date d’attribution :</strong>{" "}
          {formatDate(grant.granted_at)}
        </p>
      )}

      {grant.revoked_at && (
        <p>
          <strong>Date de révocation :</strong>{" "}
          {formatDate(grant.revoked_at)}
        </p>
      )}

      {grant.revoke_reason && (
        <p>
          <strong>
            Motif de révocation :
          </strong>{" "}
          {grant.revoke_reason}
        </p>
      )}
    </>
  );
}

function AuditLogCard({ log }) {
  const action =
    log.action ??
    log.event_type ??
    log.event ??
    log.operation ??
    "Événement";

  const actor =
    log.actor_email ??
    log.user_email ??
    log.actor ??
    log.performed_by ??
    "Non précisé";

  const target =
    log.entity_type && log.entity_id
      ? `${log.entity_type} #${log.entity_id}`
      : "Non précisée";

  const date = getAuditDate(log);

  const details =
    log.details ??
    log.description ??
    log.message ??
    null;

  return (
    <article style={styles.auditCard}>
      <div style={styles.auditHeader}>
        <h3 style={styles.auditTitle}>
          {action}
        </h3>

        <span style={styles.auditDate}>
          {date
            ? formatDate(date)
            : "Date non précisée"}
        </span>
      </div>

      <p>
        <strong>Acteur :</strong> {actor}
      </p>

      <p>
        <strong>Cible :</strong> {target}
      </p>

      {log.outcome && (
        <p>
          <strong>Résultat :</strong> {log.outcome}
        </p>
      )}

      {log.status && (
        <p>
          <strong>Statut :</strong>{" "}
          <StatusBadge status={log.status} />
        </p>
      )}

      {details && (
        <p>
          <strong>Détails :</strong>{" "}
          {typeof details === "string"
            ? details
            : JSON.stringify(
                details,
                null,
                2
              )}
        </p>
      )}
    </article>
  );
}

function getAuditDate(log) {
  return (
    log.created_at ??
    log.timestamp ??
    log.occurred_at ??
    log.date ??
    null
  );
}

function formatDate(value) {
  if (!value) {
    return "Non précisée";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString("fr-FR");
}

const styles = {
  page: {
    minHeight: "100vh",
    padding: "40px 20px",
    background: "#0d1117",
    color: "#f0f6fc",
    fontFamily: "Arial, sans-serif",
  },

  container: {
    maxWidth: "1100px",
    margin: "0 auto",
  },

  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: "20px",
    marginBottom: "30px",
    flexWrap: "wrap",
  },

  title: {
    margin: 0,
    fontSize: "48px",
  },

  subtitle: {
    marginTop: "4px",
    color: "#a5b4c3",
    fontSize: "20px",
  },

  card: {
    padding: "28px",
    marginBottom: "25px",
    border: "1px solid #30363d",
    borderRadius: "16px",
    background: "#161b22",
  },

  sessionCard: {
    padding: "24px",
    marginBottom: "25px",
    textAlign: "center",
    border: "1px solid #30363d",
    borderRadius: "16px",
    background: "#161b22",
  },

  sectionTitle: {
    marginTop: "28px",
    marginBottom: "18px",
  },

  grid: {
    display: "grid",
    gridTemplateColumns:
      "repeat(auto-fit, minmax(280px, 1fr))",
    gap: "18px",
  },

  itemCard: {
    padding: "24px",
    marginBottom: "18px",
    border: "1px solid #30363d",
    borderRadius: "14px",
    background: "#0d1117",
  },

  form: {
    display: "flex",
    flexDirection: "column",
    gap: "18px",
  },

  label: {
    display: "flex",
    flexDirection: "column",
    gap: "8px",
    fontWeight: "bold",
  },

  input: {
    padding: "13px",
    border: "1px solid #484f58",
    borderRadius: "8px",
    background: "#0d1117",
    color: "white",
    fontSize: "16px",
  },

  textarea: {
    width: "100%",
    minHeight: "100px",
    marginTop: "14px",
    padding: "13px",
    boxSizing: "border-box",
    border: "1px solid #484f58",
    borderRadius: "8px",
    background: "#0d1117",
    color: "white",
    fontSize: "16px",
  },

  buttonRow: {
    display: "flex",
    gap: "12px",
    marginTop: "14px",
  },

  primaryButton: {
    padding: "13px 18px",
    border: 0,
    borderRadius: "8px",
    background: "#6ea8fe",
    color: "#0d1117",
    fontWeight: "bold",
    cursor: "pointer",
  },

  requestButton: {
    width: "100%",
    padding: "12px",
    border: 0,
    borderRadius: "8px",
    background: "#238636",
    color: "white",
    fontWeight: "bold",
    cursor: "pointer",
  },

  approveButton: {
    flex: 1,
    padding: "12px",
    border: 0,
    borderRadius: "8px",
    background: "#238636",
    color: "white",
    fontWeight: "bold",
    cursor: "pointer",
  },

  rejectButton: {
    flex: 1,
    padding: "12px",
    border: 0,
    borderRadius: "8px",
    background: "#da3633",
    color: "white",
    fontWeight: "bold",
    cursor: "pointer",
  },

  grantButton: {
    width: "100%",
    marginTop: "14px",
    padding: "12px",
    border: 0,
    borderRadius: "8px",
    background: "#1f6feb",
    color: "white",
    fontWeight: "bold",
    cursor: "pointer",
  },

  revokeButton: {
    width: "100%",
    marginTop: "14px",
    padding: "12px",
    border: 0,
    borderRadius: "8px",
    background: "#da3633",
    color: "white",
    fontWeight: "bold",
    cursor: "pointer",
  },

  logoutButton: {
    padding: "12px 18px",
    border: "1px solid #ff7b72",
    borderRadius: "8px",
    background: "transparent",
    color: "#ff7b72",
    cursor: "pointer",
  },

  refreshButton: {
    padding: "11px 16px",
    border: "1px solid #58a6ff",
    borderRadius: "8px",
    background: "transparent",
    color: "#58a6ff",
    fontWeight: "bold",
    cursor: "pointer",
  },

  securityHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: "16px",
    flexWrap: "wrap",
  },

  securitySummary: {
    display: "grid",
    gridTemplateColumns:
      "repeat(auto-fit, minmax(180px, 1fr))",
    gap: "16px",
    marginBottom: "28px",
  },

  summaryCard: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: "8px",
    padding: "22px",
    border: "1px solid #30363d",
    borderRadius: "14px",
    background: "#161b22",
  },

  summaryValue: {
    fontSize: "34px",
    color: "#58a6ff",
  },

  summaryLabel: {
    color: "#a5b4c3",
    fontWeight: "bold",
  },

  auditCard: {
    padding: "20px",
    marginBottom: "14px",
    border: "1px solid #30363d",
    borderLeft: "4px solid #a371f7",
    borderRadius: "12px",
    background: "#161b22",
  },

  auditHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: "14px",
    flexWrap: "wrap",
  },

  auditTitle: {
    margin: 0,
    color: "#d2a8ff",
  },

  auditDate: {
    color: "#8b949e",
    fontSize: "14px",
  },

  activeStatus: {
    display: "inline-block",
    padding: "4px 8px",
    borderRadius: "999px",
    background: "rgba(35, 134, 54, 0.2)",
    color: "#7ee787",
    fontWeight: "bold",
  },

  revokedStatus: {
    display: "inline-block",
    padding: "4px 8px",
    borderRadius: "999px",
    background: "rgba(218, 54, 51, 0.2)",
    color: "#ff7b72",
    fontWeight: "bold",
  },

  pendingStatus: {
    display: "inline-block",
    padding: "4px 8px",
    borderRadius: "999px",
    background: "rgba(210, 153, 34, 0.2)",
    color: "#e3b341",
    fontWeight: "bold",
  },

  defaultStatus: {
    display: "inline-block",
    padding: "4px 8px",
    borderRadius: "999px",
    background: "rgba(110, 118, 129, 0.2)",
    color: "#c9d1d9",
    fontWeight: "bold",
  },

  empty: {
    padding: "20px",
    color: "#8b949e",
    textAlign: "center",
  },

  message: {
    textAlign: "center",
    fontSize: "17px",
    fontWeight: "bold",
    marginTop: "24px",
  },
};

export default App;